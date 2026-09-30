"""region_master 전국 채우기: 관광빅데이터·TourAPI·SGIS 의 시군구 코드를 한 행으로 잇는다.

실행: python collector/regions.py

- 기준은 관광빅데이터 최신 공개일의 시군구 목록(269개)이다.
- TourAPI 법정동 코드는 관광빅데이터 코드와 같은 체계다 (11110 = lDongRegnCd 11 + lDongSignguCd 110).
- SGIS 경계(2025)는 코드 체계가 달라 시도 + 시군구 이름으로 잇는다.
- 일반구(예: 수원시 장안구)는 parent_region_id 로 상위 시를 가리킨다. 순위·API 는 시 단위만 쓴다.
결과는 db/region_master.csv 에도 저장해 검토·문서용으로 쓴다.
"""
import csv
import json

from common import (DATALAB_URL, RAW_DIR, ROOT, SGIS_URL, TOUR_URL, connect, fetch_all,
                    find_latest_visitor_date, http_get, save_raw, sgis_token)

SGIS_YEAR = "2025"   # 2026 경계는 아직 없다 (2026-09 기준)

# SGIS 시도 코드 → 관광빅데이터 시도 코드. 광주(24)·전남(36)은 2026 통합으로 12
SGIS_SIDO = {
    "11": "11", "21": "26", "22": "27", "23": "28", "24": "12", "25": "30", "26": "31", "29": "36",
    "31": "41", "32": "51", "33": "43", "34": "44", "35": "52", "36": "12", "37": "47", "38": "48", "39": "50",
}
SGIS_NAME_FIX = {"세종시": "세종특별자치시"}

UPSERT = """
INSERT INTO region_master (sido_nm, signgu_nm, datalab_code, ldong_regn_cd, ldong_signgu_cd, sgis_code)
VALUES (%(sido_nm)s, %(signgu_nm)s, %(datalab_code)s, %(ldong_regn_cd)s, %(ldong_signgu_cd)s, %(sgis_code)s)
ON CONFLICT (datalab_code) DO UPDATE SET
    sido_nm = EXCLUDED.sido_nm,
    signgu_nm = EXCLUDED.signgu_nm,
    ldong_regn_cd = EXCLUDED.ldong_regn_cd,
    ldong_signgu_cd = EXCLUDED.ldong_signgu_cd,
    sgis_code = EXCLUDED.sgis_code
"""

SET_PARENT = """
UPDATE region_master c SET parent_region_id = p.region_id
FROM region_master p
WHERE c.datalab_code = %s AND p.datalab_code = %s
"""


def sgis_features() -> list[dict]:
    """SGIS 시군구 경계. 한 번 받으면 collector/data/raw/ 에 두고 다시 쓴다 (약 45MB, 지도 만들 때도 씀)."""
    path = RAW_DIR / f"sgis_sigungu_{SGIS_YEAR}.geojson"
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))["features"]
    token = sgis_token()
    url = f"{SGIS_URL}/boundary/hadmarea.geojson"
    sido = http_get(url, {"accessToken": token, "year": SGIS_YEAR, "low_search": "1"}, "SGIS 시도").json()
    features = []
    for f in sido["features"]:
        cd = f["properties"]["adm_cd"]
        features += http_get(url, {"accessToken": token, "year": SGIS_YEAR, "adm_cd": cd, "low_search": "1"},
                             f"SGIS {cd}").json()["features"]
    save_raw(path.name, {"type": "FeatureCollection", "features": features})
    return features


def main():
    # 1) 관광빅데이터: 최신 공개일 하루치로 시군구 목록을 얻는다
    ymd = find_latest_visitor_date().strftime("%Y%m%d")
    names = {str(r["signguCode"]): r["signguNm"]
             for r in fetch_all(DATALAB_URL, "locgoRegnVisitrDDList", "DATA_LAB_KEY", startYmd=ymd, endYmd=ymd)}

    # 2) TourAPI 법정동 코드. 세종만 lDongRegnCd 가 5자리(36110)로 온다
    ldong, sido_nm = {}, {}
    for r in fetch_all(TOUR_URL, "ldongCode2", "TOUR_API_KEY", lDongListYn="Y"):
        regn, sgg = str(r["lDongRegnCd"]), str(r["lDongSignguCd"])
        code = regn + sgg if len(regn) == 2 else sgg
        ldong[code] = (regn, sgg)
        sido_nm[code[:2]] = r["lDongRegnNm"]

    # 3) SGIS 경계: (시도, 이름) 으로 매칭
    by_name = {(code[:2], nm): code for code, nm in names.items()}
    sgis, sgis_unmatched = {}, []
    for f in sgis_features():
        cd, full = f["properties"]["adm_cd"], f["properties"]["adm_nm"]
        short = full.split(" ", 1)[1] if " " in full else full
        code = by_name.get((SGIS_SIDO[cd[:2]], SGIS_NAME_FIX.get(short, short)))
        if code:
            sgis[code] = cd
        else:
            sgis_unmatched.append(full)

    # 4) 일반구 → 상위 시 ("수원시 장안구" → "수원시")
    parent = {code: by_name[(code[:2], nm.split(" ")[0])] for code, nm in names.items() if " " in nm}

    rows = []
    for code, nm in sorted(names.items()):
        regn, sgg = ldong.get(code, (None, None))
        is_parent_city = code in parent.values()
        if is_parent_city:
            note = "일반구가 있는 시: 하위 구 경계를 합쳐 그림"
        elif code in parent:
            note = "일반구: 상위 시로 집계"
        elif code not in sgis:
            note = f"SGIS {SGIS_YEAR} 경계 없음 (2026 행정구역 개편)"
        else:
            note = ""
        rows.append({
            "datalab_code": code, "sido_nm": sido_nm.get(code[:2], ""), "signgu_nm": nm,
            "ldong_regn_cd": regn, "ldong_signgu_cd": sgg, "sgis_code": sgis.get(code),
            "parent_code": parent.get(code), "note": note,
        })

    with connect() as conn:
        with conn.cursor() as cur:
            cur.executemany(UPSERT, rows)
            cur.execute("UPDATE region_master SET parent_region_id = NULL")
            cur.executemany(SET_PARENT, [(c, p) for c, p in parent.items()])
            stale = cur.execute("SELECT datalab_code, signgu_nm FROM region_master WHERE NOT (datalab_code = ANY(%s))",
                                (list(names),)).fetchall()
        conn.commit()

    out = ROOT / "db" / "region_master.csv"
    with out.open("w", encoding="utf-8-sig", newline="") as f:   # utf-8-sig: 엑셀에서 한글이 안 깨지게
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    top = [r for r in rows if not r["parent_code"]]
    no_boundary = [r for r in top if not r["sgis_code"] and r["datalab_code"] not in parent.values()]
    print(f"기준일 {ymd}: 시군구 {len(rows)}개 = 시 단위 {len(top)}개 + 일반구 {len(parent)}개")
    print(f"TourAPI 코드 없음: {[r['signgu_nm'] for r in rows if not r['ldong_regn_cd']] or '없음'}")
    print(f"SGIS 경계 매칭 {len(sgis)}개. 매칭 안 된 SGIS: {sgis_unmatched}")
    print(f"시 단위 중 경계를 그릴 수 없는 곳: {[r['sido_nm'] + ' ' + r['signgu_nm'] for r in no_boundary]}")
    if stale:
        print(f"주의: 최신 목록에 없는 기존 지역 {stale} (삭제하지 않음)")
    print(f"저장: region_master {len(rows)}행, {out.relative_to(ROOT)}")


if __name__ == "__main__":
    try:
        main()
    except RuntimeError as e:
        raise SystemExit(f"중단: {e}\n다시 실행하면 됩니다 (중복 없음).")
