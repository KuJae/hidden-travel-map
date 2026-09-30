"""지도용 시군구 경계 파일 만들기: SGIS 2025 경계 → frontend/data/sigungu.geojson

실행: python collector/build_geojson.py   (regions.py 를 먼저 실행해 db/region_master.csv 와 SGIS 원본이 있어야 함)

- 좌표계를 UTM-K(EPSG:5179) 에서 경위도(EPSG:4326)로 바꾼다. Leaflet 은 경위도만 그린다.
- 일반구 경계는 상위 시로 합친다 (시 단위 230곳).
- 2026년 7월 개편으로 생긴 인천 4개 구는 2025 경계에 없어서, 옛 중구·동구·서구의 읍면동 경계를 합쳐 만든다.
- 용량을 줄이려고 도형을 단순화하고 좌표를 소수 4자리(약 10m)로 줄인다.
각 도형의 code 는 관광빅데이터 시군구 코드라서 API(/regions)의 code 와 그대로 연결된다.
"""
import csv
import json

from pyproj import Transformer
from shapely.geometry import mapping, shape
from shapely.ops import transform, unary_union

from common import RAW_DIR, ROOT, SGIS_URL, http_get, save_raw, sgis_token

SGIS_YEAR = "2025"
SIMPLIFY_M = 120   # 단순화 허용 오차(미터). 전국 지도 배율에서는 눈에 띄지 않는다
OUT = ROOT / "frontend" / "data" / "sigungu.geojson"

# 인천 2026 개편: 옛 구(SGIS 코드)의 읍면동을 새 구(관광빅데이터 코드)로 나눈다
INCHEON_OLD = {"23010": "중구", "23020": "동구", "23080": "서구"}
YEONGJONG = {"영종동", "영종1동", "영종2동", "운서동", "용유동"}                        # 중구 영종도 일대
GEOMDAN = {"검단동", "불로대곡동", "오류왕길동", "당하동", "마전동", "원당동", "아라동"}   # 서구 아라뱃길 북쪽


def incheon_target(gu_cd: str, dong: str) -> str:
    if gu_cd == "23010":
        return "28155" if dong in YEONGJONG else "28125"   # 영종구 / 제물포구
    if gu_cd == "23020":
        return "28125"                                     # 동구 전체 → 제물포구
    return "28290" if dong in GEOMDAN else "28275"         # 검단구 / 서해구


def incheon_dongs() -> list[dict]:
    path = RAW_DIR / f"sgis_incheon_dong_{SGIS_YEAR}.geojson"
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))["features"]
    token, feats = sgis_token(), []
    for cd in INCHEON_OLD:
        feats += http_get(f"{SGIS_URL}/boundary/hadmarea.geojson",
                          {"accessToken": token, "year": SGIS_YEAR, "adm_cd": cd, "low_search": "1"},
                          f"SGIS 인천 {cd} 읍면동").json()["features"]
    save_raw(path.name, {"type": "FeatureCollection", "features": feats})
    return feats


def main():
    rows = list(csv.DictReader((ROOT / "db" / "region_master.csv").open(encoding="utf-8-sig")))
    info = {r["datalab_code"]: r for r in rows}
    # SGIS 코드 → 시 단위 관광빅데이터 코드 (일반구는 상위 시 코드)
    target = {r["sgis_code"]: (r["parent_code"] or r["datalab_code"]) for r in rows if r["sgis_code"]}

    sgis_path = RAW_DIR / f"sgis_sigungu_{SGIS_YEAR}.geojson"
    if not sgis_path.exists():
        raise SystemExit("SGIS 경계 원본이 없습니다. python collector/regions.py 를 먼저 실행하세요.")
    parts: dict[str, list] = {}
    for f in json.loads(sgis_path.read_text(encoding="utf-8"))["features"]:
        code = target.get(f["properties"]["adm_cd"])
        if code:
            parts.setdefault(code, []).append(shape(f["geometry"]))
    for f in incheon_dongs():
        cd = f["properties"]["adm_cd"]
        code = incheon_target(cd[:5], f["properties"]["adm_nm"].split()[-1])
        parts.setdefault(code, []).append(shape(f["geometry"]))

    to_wgs84 = Transformer.from_crs(5179, 4326, always_xy=True).transform
    features = []
    for code, geoms in sorted(parts.items()):
        geom = unary_union(geoms).buffer(0).simplify(SIMPLIFY_M, preserve_topology=True)
        geom = transform(to_wgs84, geom)
        gj = json.loads(json.dumps(mapping(geom)), parse_float=lambda s: round(float(s), 4))
        r = info[code]
        features.append({"type": "Feature", "properties": {"code": code, "sido_nm": r["sido_nm"], "signgu_nm": r["signgu_nm"]},
                         "geometry": gj})

    top = {r["datalab_code"] for r in rows if not r["parent_code"]}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({"type": "FeatureCollection", "features": features}, ensure_ascii=False, separators=(",", ":")),
                   encoding="utf-8")
    print(f"시군구 경계 {len(features)}개 (시 단위 {len(top)}곳 중 경계 없음: {sorted(top - parts.keys()) or '없음'})")
    print(f"인천 신설 구: {[info[c]['signgu_nm'] for c in ('28125', '28155', '28275', '28290') if c in parts]}")
    print(f"저장: {OUT.relative_to(ROOT)} ({OUT.stat().st_size / 1e6:.2f}MB)")


if __name__ == "__main__":
    main()
