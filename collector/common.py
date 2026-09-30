"""수집기 공통 모듈: .env 읽기, 공공데이터포털·SGIS 호출, DB 연결."""
import json
import os
from datetime import date, timedelta
from pathlib import Path
from urllib.parse import unquote

import requests
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = Path(__file__).resolve().parent / "data" / "raw"
load_dotenv(ROOT / ".env")

DATALAB_URL = "https://apis.data.go.kr/B551011/DataLabService"   # 관광빅데이터 (지역별 방문자수)
TOUR_URL = "https://apis.data.go.kr/B551011/KorService2"         # 국문 관광정보 (TourAPI)
SGIS_URL = "https://sgisapi.mods.go.kr/OpenAPI3"                 # 옛 주소 sgisapi.kostat.go.kr 는 여기로 리다이렉트됨

# 관광빅데이터 touDivCd
LOCAL, OUTSIDER, FOREIGNER = 1, 2, 3


def env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise SystemExit(f".env 에 {name} 값이 없습니다. .env.example 을 참고해 채워 주세요.")
    return value


def call_data_go_kr(base: str, operation: str, key_name: str, **params) -> dict:
    """공공데이터포털 API 한 페이지를 불러 response.body 를 돌려준다. 오류면 원인을 담아 중단한다."""
    query = {
        # Encoding 키를 넣어도 되도록 한 번 풀어 준다 (requests 가 다시 인코딩한다)
        "serviceKey": unquote(env(key_name)),
        "MobileOS": "ETC",
        "MobileApp": "HiddenTravelMap",
        "_type": "json",
        **params,
    }
    res = requests.get(f"{base}/{operation}", params=query, timeout=30)
    try:
        data = res.json()
    except ValueError:
        raise RuntimeError(f"{operation}: JSON 이 아닌 응답 (HTTP {res.status_code}) {res.text[:300]}")

    # 키 없음·미승인·트래픽 초과 같은 게이트웨이 오류는 모양이 다르다
    if "OpenAPI_ServiceResponse" in data:
        h = data["OpenAPI_ServiceResponse"]["cmmMsgHeader"]
        raise RuntimeError(f"{operation}: {h.get('errMsg')} ({h.get('returnAuthMsg')})")

    header = data["response"]["header"]
    if header["resultCode"] not in ("0000", "00"):
        raise RuntimeError(f"{operation}: {header['resultCode']} {header['resultMsg']}")
    return data["response"]["body"]


def items_of(body: dict) -> list[dict]:
    """body.items.item 을 항상 리스트로 바꾼다. 결과가 없으면 items 가 "" 로, 1건이면 dict 로 온다."""
    items = body.get("items")
    if not isinstance(items, dict):
        return []
    item = items.get("item") or []
    return item if isinstance(item, list) else [item]


def fetch_all(base: str, operation: str, key_name: str, num_of_rows: int = 1000, **params) -> list[dict]:
    """pageNo 를 올려 가며 totalCount 만큼 모두 받는다."""
    rows, page = [], 1
    while True:
        body = call_data_go_kr(base, operation, key_name, numOfRows=num_of_rows, pageNo=page, **params)
        rows += items_of(body)
        if page * num_of_rows >= int(body.get("totalCount") or 0):
            return rows
        page += 1


def find_latest_visitor_date(start_back: int = 20, max_back: int = 70) -> date:
    """관광빅데이터는 약 1개월 늦게 공개된다. 오늘부터 거슬러 올라가며 데이터가 있는 가장 최근 날짜를 찾는다."""
    for back in range(start_back, max_back + 1):
        day = date.today() - timedelta(days=back)
        ymd = day.strftime("%Y%m%d")
        body = call_data_go_kr(DATALAB_URL, "locgoRegnVisitrDDList", "DATA_LAB_KEY",
                               numOfRows=1, pageNo=1, startYmd=ymd, endYmd=ymd)
        if int(body.get("totalCount") or 0) > 0:
            return day
    raise RuntimeError(f"최근 {max_back}일 안에 공개된 방문자 데이터가 없습니다.")


def sgis_token() -> str:
    res = requests.get(f"{SGIS_URL}/auth/authentication.json", timeout=30, params={
        "consumer_key": env("SGIS_SERVICE_ID"),
        "consumer_secret": env("SGIS_SECRET_KEY"),
    })
    data = res.json()
    if str(data.get("errCd")) != "0":
        raise RuntimeError(f"SGIS 인증 실패: {data.get('errCd')} {data.get('errMsg')}")
    return data["result"]["accessToken"]


def save_raw(name: str, data) -> Path:
    """원본 응답을 collector/data/raw/ 에 저장한다 (커밋되지 않음)."""
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    path = RAW_DIR / name
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def connect():
    import psycopg

    # prepare_threshold=None: Supabase pooler 에서 prepared statement 오류가 나지 않게 한다
    return psycopg.connect(env("DATABASE_URL"), prepare_threshold=None)
