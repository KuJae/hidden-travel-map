"""TourAPI 관광지 수집 → attractions 저장 (대표 사진이 있는 콘텐츠만).

실행: python collector/attractions.py

region_master 의 시도(lDongRegnCd)마다 한 번에 받아, 등록된 시군구의 콘텐츠만 저장한다.
옛 areaCode/sigunguCode 는 비어 있는 콘텐츠가 많아 반드시 법정동 코드(lDong*)로 조회·매칭한다.
"""
from common import TOUR_URL, connect, fetch_all

# 음식점·숙박·쇼핑·여행코스는 제외 범위라 받지 않는다
CONTENT_TYPES = {"12": "관광지", "14": "문화시설", "28": "레포츠"}

UPSERT = """
INSERT INTO attractions (content_id, region_id, title, category, address, lat, lon, image_url, updated_at)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, now())
ON CONFLICT (content_id) DO UPDATE SET
    region_id = EXCLUDED.region_id,
    title = EXCLUDED.title,
    category = EXCLUDED.category,
    address = EXCLUDED.address,
    lat = EXCLUDED.lat,
    lon = EXCLUDED.lon,
    image_url = EXCLUDED.image_url,
    updated_at = now()
"""


def to_float(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def main():
    with connect() as conn:
        rows = conn.execute("""
            SELECT ldong_regn_cd, ldong_signgu_cd, region_id FROM region_master
            WHERE ldong_regn_cd IS NOT NULL AND ldong_signgu_cd IS NOT NULL
        """).fetchall()
        regions = {(regn, sgg): region_id for regn, sgg, region_id in rows}
        if not regions:
            raise SystemExit("region_master 에 법정동 코드가 있는 지역이 없습니다. db/schema.sql 을 먼저 실행하세요.")

        for regn in sorted({regn for regn, _ in regions}):
            for type_id, type_nm in CONTENT_TYPES.items():
                # arrange=Q: 대표 이미지가 있는 콘텐츠만, 수정일순
                items = fetch_all(TOUR_URL, "areaBasedList2", "TOUR_API_KEY",
                                  lDongRegnCd=regn, contentTypeId=type_id, arrange="Q")
                batch = []
                for it in items:
                    region_id = regions.get((str(it.get("lDongRegnCd")), str(it.get("lDongSignguCd"))))
                    if region_id is None or not it.get("firstimage"):
                        continue
                    batch.append((
                        str(it["contentid"]), region_id, it["title"], type_nm, it.get("addr1") or None,
                        to_float(it.get("mapy")), to_float(it.get("mapx")), it["firstimage"],
                    ))
                with conn.cursor() as cur:
                    cur.executemany(UPSERT, batch)
                conn.commit()
                print(f"  시도 {regn} {type_nm}: 받음 {len(items)}건, 저장 {len(batch)}건")

        for nm, cnt in conn.execute("""
            SELECT r.signgu_nm, count(a.content_id) FROM region_master r
            LEFT JOIN attractions a USING (region_id) GROUP BY r.signgu_nm ORDER BY 2 DESC
        """).fetchall():
            print(f"{nm}: 사진 있는 관광지 {cnt}곳")


if __name__ == "__main__":
    try:
        main()
    except RuntimeError as e:
        raise SystemExit(f"중단: {e}\n다시 실행하면 중복 없이 이어서 저장합니다.")
