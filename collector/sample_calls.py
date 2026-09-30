"""외부 API 3종을 한 번씩 불러 응답 모양을 확인한다 (DB 에는 저장하지 않는다).

실행: python collector/sample_calls.py            # 3종 모두
      python collector/sample_calls.py datalab    # 하나만 (datalab / tour / sgis)
원본 응답은 collector/data/raw/ 에 저장된다. 키가 없는 API 는 건너뛰고 이유를 출력한다.
"""
import sys
from collections import Counter

import requests

from common import (DATALAB_URL, ROOT, SGIS_URL, TOUR_URL, call_data_go_kr, fetch_all,
                    find_latest_visitor_date, http_get, items_of, save_raw, sgis_token)


def sample_datalab():
    print("\n[1] 관광빅데이터 locgoRegnVisitrDDList")
    day = find_latest_visitor_date()
    ymd = day.strftime("%Y%m%d")
    rows = fetch_all(DATALAB_URL, "locgoRegnVisitrDDList", "DATA_LAB_KEY", startYmd=ymd, endYmd=ymd)
    path = save_raw(f"datalab_{ymd}.json", rows)
    print(f"  최신 공개일 {day}, 하루 {len(rows)}행 → {path.relative_to(ROOT)}")
    print(f"  필드: {list(rows[0].keys())}")
    print(f"  시군구 수: {len({r.get('signguCode') for r in rows})}, "
          f"touDivCd 분포: {dict(Counter(str(r.get('touDivCd')) for r in rows))}")
    print(f"  touNum 타입: {type(rows[0].get('touNum')).__name__} (예: {rows[0].get('touNum')!r})")
    for r in rows:
        if "종로" in str(r.get("signguNm")):
            print(f"  종로구 → signguCode={r.get('signguCode')} touDivCd={r.get('touDivCd')} touNum={r.get('touNum')}")


def sample_tour():
    print("\n[2] TourAPI ldongCode2 (서울 시군구 법정동 코드)")
    codes = items_of(call_data_go_kr(TOUR_URL, "ldongCode2", "TOUR_API_KEY",
                                     numOfRows=100, pageNo=1, lDongRegnCd="11"))
    save_raw("tour_ldong_11.json", codes)
    print(f"  {len(codes)}건, 필드: {list(codes[0].keys()) if codes else '-'}")
    print(f"  종로 → {[c for c in codes if '종로' in str(c.values())]}")

    print("\n[2] TourAPI areaBasedList2 (종로구 관광지 첫 페이지)")
    body = call_data_go_kr(TOUR_URL, "areaBasedList2", "TOUR_API_KEY", numOfRows=100, pageNo=1,
                           lDongRegnCd="11", lDongSignguCd="110", contentTypeId="12")
    items = items_of(body)
    path = save_raw("tour_jongno_12.json", items)
    with_image = [it for it in items if it.get("firstimage")]
    print(f"  전체 {body.get('totalCount')}건 중 첫 페이지 {len(items)}건, 사진 있음 {len(with_image)}건 → {path.relative_to(ROOT)}")
    if items:
        print(f"  필드: {list(items[0].keys())}")
        print(f"  옛 sigunguCode 가 빈 콘텐츠: {sum(1 for it in items if not it.get('sigunguCode'))}건")
    for it in with_image[:3]:
        print(f"  - {it.get('title')} | {it.get('addr1')} | ({it.get('mapy')}, {it.get('mapx')}) | "
              f"lDong={it.get('lDongRegnCd')}/{it.get('lDongSignguCd')}")


def _first_xy(coords):
    while isinstance(coords[0], list):
        coords = coords[0]
    return coords[0], coords[1]


def sample_sgis():
    print("\n[3] SGIS hadmarea.geojson (서울 시군구 경계)")
    token = sgis_token()
    for year in ("2025", "2024", "2023"):
        data = http_get(f"{SGIS_URL}/boundary/hadmarea.geojson", {
            "accessToken": token, "year": year, "adm_cd": "11", "low_search": "1",
        }, "SGIS 경계").json()
        if data.get("features"):
            break
        print(f"  year={year}: {data.get('errCd')} {data.get('errMsg')}")
    else:
        raise RuntimeError("경계 데이터를 받지 못했습니다.")
    path = save_raw(f"sgis_seoul_{year}.geojson", data)
    feats = data["features"]
    print(f"  기준연도 {year}, {len(feats)}개 → {path.relative_to(ROOT)}")
    print(f"  properties: {feats[0]['properties']}")
    print(f"  종로 → {[f['properties'] for f in feats if '종로' in str(f['properties'])]}")
    x, y = _first_xy(feats[0]["geometry"]["coordinates"])
    crs = "UTM-K(EPSG:5179) → 지도용 파일은 EPSG:4326 변환 필요" if abs(x) > 1000 else "경위도(WGS84)"
    print(f"  첫 좌표 ({x}, {y}) → {crs}")


SAMPLES = {"datalab": sample_datalab, "tour": sample_tour, "sgis": sample_sgis}

if __name__ == "__main__":
    for name in sys.argv[1:] or SAMPLES:
        try:
            SAMPLES[name]()
        except (RuntimeError, SystemExit, requests.RequestException) as e:
            print(f"  실패: {e}")
