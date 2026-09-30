"""관광빅데이터 방문자 수 수집 → visitor_daily 저장 → visitor_summary 재계산.

실행: python collector/visitors.py              # 최신 공개일 기준 30일
      python collector/visitors.py --days 7     # 기간 조절 (API 호출 수 ≈ 일수 + 최신일 탐색 몇 번)

API 가 전국 시군구를 한 번에 주므로, region_master 에 등록된 지역만 골라 저장한다.
같은 기간을 다시 돌려도 (지역, 날짜, 관광객 구분) 키 덕분에 중복 저장되지 않는다.
"""
import argparse
from datetime import datetime, timedelta
from decimal import Decimal

from common import DATALAB_URL, connect, fetch_all, find_latest_visitor_date

UPSERT = """
INSERT INTO visitor_daily (region_id, base_date, visitor_type, visitor_count)
VALUES (%s, %s, %s, %s)
ON CONFLICT (region_id, base_date, visitor_type)
DO UPDATE SET visitor_count = EXCLUDED.visitor_count
"""

# 가장 최근 날짜부터 N일 창에서 외지인(2)+외국인(3) 일평균 → 전국 백분위 → Ghost Index
SUMMARY = """
WITH win AS (
    SELECT max(base_date) AS end_date FROM visitor_daily
), daily AS (
    SELECT v.region_id, v.base_date, sum(v.visitor_count) AS cnt
    FROM visitor_daily v, win
    WHERE v.visitor_type IN (2, 3) AND v.base_date > win.end_date - %(days)s::int
    GROUP BY v.region_id, v.base_date
), avg_by_region AS (
    SELECT region_id, min(base_date) AS ws, max(base_date) AS we, avg(cnt) AS avg_cnt
    FROM daily GROUP BY region_id
), ranked AS (
    SELECT *, round((100 * percent_rank() OVER (ORDER BY avg_cnt))::numeric, 1) AS pct
    FROM avg_by_region
)
INSERT INTO visitor_summary
    (region_id, window_start, window_end, avg_daily_visitors, percentile, ghost_index, updated_at)
SELECT region_id, ws, we, round(avg_cnt, 1), pct, 100 - pct, now() FROM ranked
ON CONFLICT (region_id) DO UPDATE SET
    window_start = EXCLUDED.window_start,
    window_end = EXCLUDED.window_end,
    avg_daily_visitors = EXCLUDED.avg_daily_visitors,
    percentile = EXCLUDED.percentile,
    ghost_index = EXCLUDED.ghost_index,
    updated_at = EXCLUDED.updated_at
"""


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--days", type=int, default=30)
    args = parser.parse_args()

    with connect() as conn:
        regions = dict(conn.execute("SELECT datalab_code, region_id FROM region_master").fetchall())
        if not regions:
            raise SystemExit("region_master 가 비어 있습니다. db/schema.sql 을 먼저 실행하세요.")

        end = find_latest_visitor_date()
        print(f"최신 공개일 {end}부터 {args.days}일, 대상 지역 {len(regions)}곳")

        saved, unmatched = 0, set()
        for back in range(args.days):
            ymd = (end - timedelta(days=back)).strftime("%Y%m%d")
            rows = fetch_all(DATALAB_URL, "locgoRegnVisitrDDList", "DATA_LAB_KEY", startYmd=ymd, endYmd=ymd)
            batch = []
            for r in rows:
                region_id = regions.get(str(r["signguCode"]))
                if region_id is None:
                    unmatched.add(str(r["signguCode"]))
                    continue
                batch.append((
                    region_id,
                    datetime.strptime(str(r["baseYmd"]), "%Y%m%d").date(),
                    int(r["touDivCd"]),
                    Decimal(str(r["touNum"])),   # 문자열로 온다
                ))
            with conn.cursor() as cur:
                cur.executemany(UPSERT, batch)
            conn.commit()
            saved += len(batch)
            print(f"  {ymd}: 받음 {len(rows)}행, 저장 {len(batch)}행")

        conn.execute(SUMMARY, {"days": args.days})
        conn.commit()
        print(f"완료: 저장 {saved}행, region_master 에 없는 시군구 코드 {len(unmatched)}개 (전국 확대 때 매핑 대상)")
        if len(regions) == 1:
            print("참고: 지역이 1곳뿐이라 백분위·Ghost Index 는 아직 의미가 없습니다 (전국 확대 후 의미가 생김).")

        summary = conn.execute("""
            SELECT r.signgu_nm, s.window_start, s.window_end, s.avg_daily_visitors, s.percentile, s.ghost_index
            FROM visitor_summary s JOIN region_master r USING (region_id)
            ORDER BY s.ghost_index DESC LIMIT 5
        """).fetchall()
        for nm, ws, we, avg, pct, ghost in summary:
            print(f"  {nm}: {ws}~{we} 일평균 {avg}명, 하위 {pct}%, Ghost Index {ghost}")


if __name__ == "__main__":
    main()
