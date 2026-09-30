import psycopg
from fastapi import APIRouter, Depends, HTTPException, Path, Query

from app.db import get_conn
from app.models import Attraction, RegionSummary
from app.rules import HIDDEN_MAX_PERCENTILE, HIDDEN_MIN_ATTRACTIONS

router = APIRouter(tags=["regions"])

CODE = Path(description="관광빅데이터 시군구 코드 (종로구 11110). 시 단위 코드만 받는다", examples=["11110"])

# 시 단위 지역(일반구 제외)의 방문량 요약 + 사진 있는 관광지 수 + 숨은 지역 후보 여부
# (기준값은 코드 상수라 문자열에 바로 넣는다. 사용자 입력은 여기에 들어오지 않는다)
SUMMARY_SQL = f"""
    SELECT r.datalab_code AS code, r.sido_nm, r.signgu_nm, r.sgis_code,
           s.window_start, s.window_end, s.avg_daily_visitors, s.percentile, s.ghost_index,
           COALESCE(a.cnt, 0) AS attraction_count,
           COALESCE(s.percentile <= {HIDDEN_MAX_PERCENTILE} AND COALESCE(a.cnt, 0) >= {HIDDEN_MIN_ATTRACTIONS}, false)
               AS is_candidate
    FROM region_master r
    LEFT JOIN visitor_summary s USING (region_id)
    LEFT JOIN (SELECT region_id, count(*) AS cnt FROM attractions GROUP BY region_id) a USING (region_id)
    WHERE r.parent_region_id IS NULL
"""


def _region_id(conn: psycopg.Connection, code: str) -> int:
    row = conn.execute(
        "SELECT region_id FROM region_master WHERE datalab_code = %s AND parent_region_id IS NULL", (code,)
    ).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail=f"{code} 지역을 찾을 수 없습니다 (일반구는 상위 시 코드로 조회)")
    return row["region_id"]


@router.get("/regions", response_model=list[RegionSummary], summary="전국 시군구 방문량 요약 (지도 색칠용)")
def list_regions(conn: psycopg.Connection = Depends(get_conn)):
    return conn.execute(SUMMARY_SQL + " ORDER BY r.datalab_code").fetchall()


@router.get("/regions/{code}", response_model=RegionSummary, summary="선택 지역 방문량 요약")
def get_region(code: str = CODE, conn: psycopg.Connection = Depends(get_conn)):
    row = conn.execute(SUMMARY_SQL + " AND r.datalab_code = %s", (code,)).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail=f"{code} 지역을 찾을 수 없습니다 (일반구는 상위 시 코드로 조회)")
    return row


@router.get("/regions/{code}/attractions", response_model=list[Attraction], summary="선택 지역의 사진 있는 관광지")
def list_attractions(
    code: str = CODE,
    limit: int = Query(6, ge=1, le=50, description="최대 개수"),
    conn: psycopg.Connection = Depends(get_conn),
):
    region_id = _region_id(conn, code)
    return conn.execute("""
        SELECT content_id, title, category, address, lat, lon, image_url, image_license
        FROM attractions
        WHERE region_id = %s
        ORDER BY (category = '관광지') DESC, title
        LIMIT %s
    """, (region_id, limit)).fetchall()


@router.get("/hidden", response_model=list[RegionSummary], summary="숨은 지역 후보 (방문 적고 볼거리 있는 곳)")
def list_hidden(
    max_percentile: float = Query(HIDDEN_MAX_PERCENTILE, ge=0, le=100, description="방문량 하위 몇 % 까지 (팀 기준 30)"),
    min_attractions: int = Query(HIDDEN_MIN_ATTRACTIONS, ge=0, description="사진 있는 관광지 최소 개수 (팀 기준 3)"),
    limit: int = Query(20, ge=1, le=230, description="최대 개수"),
    conn: psycopg.Connection = Depends(get_conn),
):
    return conn.execute(
        SUMMARY_SQL + """
        AND s.percentile <= %s AND COALESCE(a.cnt, 0) >= %s
        ORDER BY s.ghost_index DESC, attraction_count DESC
        LIMIT %s
    """, (max_percentile, min_attractions, limit)).fetchall()
