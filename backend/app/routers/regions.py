import psycopg
from fastapi import APIRouter, Depends, HTTPException, Path, Query

from app.db import get_conn
from app.models import Attraction, RegionSummary

router = APIRouter(prefix="/regions", tags=["regions"])

CODE = Path(description="관광빅데이터 시군구 코드 (종로구 11110)", examples=["11110"])


def _region_id(conn: psycopg.Connection, code: str) -> int:
    row = conn.execute("SELECT region_id FROM region_master WHERE datalab_code = %s", (code,)).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail=f"{code} 지역을 찾을 수 없습니다")
    return row["region_id"]


@router.get("/{code}", response_model=RegionSummary, summary="선택 지역 방문량 요약")
def get_region(code: str = CODE, conn: psycopg.Connection = Depends(get_conn)):
    row = conn.execute("""
        SELECT r.datalab_code AS code, r.sido_nm, r.signgu_nm, r.sgis_code,
               s.window_start, s.window_end, s.avg_daily_visitors, s.percentile, s.ghost_index,
               (SELECT count(*) FROM attractions a WHERE a.region_id = r.region_id) AS attraction_count
        FROM region_master r
        LEFT JOIN visitor_summary s USING (region_id)
        WHERE r.datalab_code = %s
    """, (code,)).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail=f"{code} 지역을 찾을 수 없습니다")
    return row


@router.get("/{code}/attractions", response_model=list[Attraction], summary="선택 지역의 사진 있는 관광지")
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
