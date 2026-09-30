"""분석 페이지용 집계. 모두 시 단위(일반구 제외) 기준이고, 집계 창은 visitor_summary 의 30일이다."""
import psycopg
from fastapi import APIRouter, Depends, HTTPException

from app.db import get_conn
from app.models import SidoStats, StatsOverview
from app.rules import HIDDEN_MAX_PERCENTILE as HP, HIDDEN_MIN_ATTRACTIONS as HA

router = APIRouter(prefix="/stats", tags=["stats"])

LABELS = {1: "현지인", 2: "외지인", 3: "외국인"}

# 지역별 관광객 구분 합계 (집계 창 안)
BY_REGION_TYPE = """
    SELECT v.region_id,
           COALESCE(sum(v.visitor_count) FILTER (WHERE v.visitor_type = 1), 0) AS l,
           COALESCE(sum(v.visitor_count) FILTER (WHERE v.visitor_type = 2), 0) AS o,
           COALESCE(sum(v.visitor_count) FILTER (WHERE v.visitor_type = 3), 0) AS f
    FROM visitor_daily v, (SELECT min(window_start) AS ws, max(window_end) AS we FROM visitor_summary) w
    WHERE v.base_date BETWEEN w.ws AND w.we
    GROUP BY v.region_id
"""

LOCAL_SHARE = f"""
    WITH t AS ({BY_REGION_TYPE})
    SELECT r.sido_nm, r.signgu_nm, round(100 * t.l / (t.l + t.o + t.f), 1) AS local_share
    FROM t JOIN region_master r USING (region_id)
    WHERE r.parent_region_id IS NULL
"""


@router.get("/overview", response_model=StatsOverview, summary="전국 요약 (분석 페이지용)")
def overview(conn: psycopg.Connection = Depends(get_conn)):
    win = conn.execute("SELECT min(window_start) AS ws, max(window_end) AS we FROM visitor_summary").fetchone()
    if win["we"] is None:
        raise HTTPException(status_code=404, detail="아직 집계된 방문자 데이터가 없습니다")

    counts = conn.execute(f"""
        SELECT (SELECT count(DISTINCT base_date) FROM visitor_daily WHERE base_date BETWEEN %(ws)s AND %(we)s) AS days,
               (SELECT count(*) FROM region_master WHERE parent_region_id IS NULL) AS region_count,
               (SELECT count(*) FROM region_master WHERE parent_region_id IS NOT NULL) AS subregion_count,
               (SELECT count(*) FROM attractions) AS attraction_count,
               (SELECT count(*) FROM visitor_daily) AS visitor_rows
    """, win).fetchone()

    mix = conn.execute("""
        SELECT v.visitor_type, sum(v.visitor_count) / count(DISTINCT v.base_date) AS daily_avg
        FROM visitor_daily v
        JOIN region_master r ON r.region_id = v.region_id AND r.parent_region_id IS NULL
        WHERE v.base_date BETWEEN %(ws)s AND %(we)s
        GROUP BY 1 ORDER BY 1
    """, win).fetchall()
    total = sum(m["daily_avg"] for m in mix)
    visitor_mix = [{
        "visitor_type": m["visitor_type"], "label": LABELS[m["visitor_type"]],
        "daily_avg": round(m["daily_avg"]), "share": round(100 * m["daily_avg"] / total, 1),
    } for m in mix]

    # 방문량 분포, 숨은 지역 후보 수, 볼거리(사진 수)와 방문량의 관계
    # 기준값(HP, HA)은 코드 상수라 문자열에 바로 넣는다
    dist = conn.execute(f"""
        WITH a AS (SELECT region_id, count(*) AS cnt FROM attractions GROUP BY region_id)
        SELECT percentile_cont(0.5) WITHIN GROUP (ORDER BY s.avg_daily_visitors) AS median_daily_visitors,
               max(s.avg_daily_visitors) FILTER (WHERE s.percentile <= {HP}) AS threshold_hidden,
               count(*) FILTER (WHERE s.percentile <= {HP} AND COALESCE(a.cnt, 0) >= {HA}) AS hidden_count,
               count(*) FILTER (WHERE s.percentile <= {HP} AND COALESCE(a.cnt, 0) >= {HA}
                                AND r.signgu_nm LIKE '%군') AS hidden_gun_count,
               count(*) FILTER (WHERE s.percentile <= 20 AND COALESCE(a.cnt, 0) >= {HA}) AS hidden_p20,
               corr(ln(s.avg_daily_visitors), ln(a.cnt)) AS corr_log_attractions_visitors,
               percentile_cont(0.5) WITHIN GROUP (ORDER BY COALESCE(a.cnt, 0))
                   FILTER (WHERE s.percentile <= 20) AS median_attractions_bottom20,
               percentile_cont(0.5) WITHIN GROUP (ORDER BY COALESCE(a.cnt, 0)) AS median_attractions_all,
               percentile_cont(0.5) WITHIN GROUP (ORDER BY COALESCE(a.cnt, 0))
                   FILTER (WHERE s.percentile >= 80) AS median_attractions_top20
        FROM visitor_summary s
        JOIN region_master r USING (region_id)
        LEFT JOIN a USING (region_id)
        WHERE r.parent_region_id IS NULL
    """).fetchone()

    return {
        "window_start": win["ws"], "window_end": win["we"], **counts,
        "hidden_max_percentile": HP, "hidden_min_attractions": HA,
        "visitor_mix": visitor_mix,
        "local_share_lowest": conn.execute(LOCAL_SHARE + " ORDER BY local_share LIMIT 3").fetchall(),
        "local_share_highest": conn.execute(LOCAL_SHARE + " ORDER BY local_share DESC LIMIT 3").fetchall(),
        **{k: round(float(v), 3) if k.startswith("corr") and v is not None else v for k, v in dist.items()},
    }


@router.get("/sido", response_model=list[SidoStats], summary="시도별 방문량·관광객 구성·숨은 지역 후보 수")
def by_sido(conn: psycopg.Connection = Depends(get_conn)):
    return conn.execute(f"""
        WITH a AS (SELECT region_id, count(*) AS cnt FROM attractions GROUP BY region_id),
             t AS ({BY_REGION_TYPE})
        SELECT r.sido_nm,
               count(*) AS region_count,
               percentile_cont(0.5) WITHIN GROUP (ORDER BY s.avg_daily_visitors) AS median_daily_visitors,
               round(100 * sum(t.l) / sum(t.l + t.o + t.f), 1) AS local_share,
               round(100 * sum(t.o) / sum(t.l + t.o + t.f), 1) AS outsider_share,
               round(100 * sum(t.f) / sum(t.l + t.o + t.f), 1) AS foreigner_share,
               count(*) FILTER (WHERE s.percentile <= {HP} AND COALESCE(a.cnt, 0) >= {HA}) AS hidden_count,
               COALESCE(sum(a.cnt), 0) AS attraction_count
        FROM region_master r
        JOIN visitor_summary s USING (region_id)
        JOIN t USING (region_id)
        LEFT JOIN a USING (region_id)
        WHERE r.parent_region_id IS NULL
        GROUP BY r.sido_nm
        ORDER BY median_daily_visitors
    """).fetchall()
