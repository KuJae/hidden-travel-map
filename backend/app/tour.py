"""TourAPI 관광지 상세 조회 (비교함용).

관광지마다 처음 볼 때 한 번만 부르고, 결과는 attraction_details 에 저장해 다음부터는 DB 에서 준다.
인증키는 환경변수 TOUR_API_KEY (로컬은 저장소 루트 .env, Render 는 대시보드 환경변수).
오류 메시지에는 인증키가 든 URL 이 찍히지 않게 오류 종류만 남긴다.
"""
import html
import os
import re
from urllib.parse import unquote

import httpx

TOUR_URL = "https://apis.data.go.kr/B551011/KorService2"
TYPE_ID = {"관광지": "12", "문화시설": "14", "레포츠": "28"}

# detailIntro2 는 유형마다 필드 이름이 달라서 하나로 맞춘다 (관광지 usetime, 문화시설 usetimeculture, 레포츠 usetimeleports)
INTRO_FIELDS = {
    "usetime": ("usetime", "usetimeculture", "usetimeleports"),
    "restdate": ("restdate", "restdateculture", "restdateleports"),
    "usefee": ("usefee", "usefeeleports"),
    "parking": ("parking", "parkingculture", "parkingleports"),
    "parkingfee": ("parkingfee", "parkingfeeleports"),
    "infocenter": ("infocenter", "infocenterculture", "infocenterleports"),
    "chkpet": ("chkpet", "chkpetculture", "chkpetleports"),
    "chkbabycarriage": ("chkbabycarriage", "chkbabycarriageculture", "chkbabycarriageleports"),
}

# attraction_details 에 저장하는 컬럼 (순서는 INSERT 문과 같다)
DETAIL_COLUMNS = ("overview", "homepage", "tel", "usetime", "restdate", "usefee", "parking", "chkpet", "chkbabycarriage")


class TourAPIError(RuntimeError):
    pass


def _clean(value) -> str | None:
    """<br> 은 줄바꿈으로 바꾸고 나머지 태그는 지운다. &amp; 같은 문자도 풀어 준다."""
    if value in (None, ""):
        return None
    text = re.sub(r"<br\s*/?>", "\n", str(value), flags=re.I)
    text = html.unescape(re.sub(r"<[^>]+>", "", text))
    text = "\n".join(line.strip() for line in text.splitlines() if line.strip())
    return text or None


def _homepage(value) -> str | None:
    """homepage 는 <a href="...">...</a> 문자열로 온다. 첫 http(s) 주소만 꺼낸다."""
    if not value:
        return None
    m = re.search(r"https?://[^\s\"'<>]+", html.unescape(str(value)))
    return m.group(0) if m else None


def _service_key() -> str:
    # 대시보드에 붙여 넣을 때 흔히 딸려 오는 앞뒤 공백·줄바꿈·따옴표, .env 줄째 붙인 'TOUR_API_KEY=' 를 떼어 낸다
    # (Render 에서 이런 값은 게이트웨이가 '등록되지 않은 서비스키'로 거절한다)
    key = os.getenv("TOUR_API_KEY", "").strip().strip("\"'").strip()
    return key.removeprefix("TOUR_API_KEY=").strip().strip("\"'").strip()


def _first_item(client: httpx.Client, operation: str, **params) -> dict:
    key = _service_key()
    if not key:
        raise TourAPIError("TOUR_API_KEY 가 설정되지 않았습니다")
    query = {
        "serviceKey": unquote(key),   # Encoding 키를 넣어도 되도록 한 번 풀어 준다
        "MobileOS": "ETC",
        "MobileApp": "HiddenTravelMap",
        "_type": "json",
        **params,
    }
    try:
        data = client.get(f"{TOUR_URL}/{operation}", params=query).json()
    except (httpx.HTTPError, ValueError) as e:
        raise TourAPIError(f"{operation}: {type(e).__name__}") from None

    # 키 없음·미승인·트래픽 초과 같은 게이트웨이 오류는 모양이 다르다
    if "OpenAPI_ServiceResponse" in data:
        h = data["OpenAPI_ServiceResponse"].get("cmmMsgHeader", {})
        raise TourAPIError(f"{operation}: {h.get('returnAuthMsg') or h.get('errMsg')}")
    header = data.get("response", {}).get("header", {})
    if header.get("resultCode") not in ("0000", "00"):
        raise TourAPIError(f"{operation}: {header.get('resultCode')} {header.get('resultMsg')}")

    items = data["response"]["body"].get("items")   # 결과가 없으면 "" 로, 1건이면 dict 로 온다
    if not isinstance(items, dict):
        return {}
    item = items.get("item") or []
    item = item if isinstance(item, list) else [item]
    return item[0] if item else {}


def fetch_detail(content_id: str, category: str | None) -> dict:
    """TourAPI 두 번(detailCommon2, detailIntro2)을 불러 DETAIL_COLUMNS 모양으로 돌려준다."""
    # apis.data.go.kr 가 가끔 30초 넘게 멈춰서, 화면이 오래 기다리지 않게 짧게 끊는다
    with httpx.Client(timeout=8) as client:
        common = _first_item(client, "detailCommon2", contentId=content_id)
        intro = _first_item(client, "detailIntro2", contentId=content_id,
                            contentTypeId=TYPE_ID.get(category or "", "12"))

    picked = {}
    for field, keys in INTRO_FIELDS.items():
        picked[field] = next((v for v in (_clean(intro.get(k)) for k in keys) if v), None)

    parking, fee = picked.pop("parking"), picked.pop("parkingfee")
    infocenter = picked.pop("infocenter")
    return {
        "overview": _clean(common.get("overview")),
        "homepage": _homepage(common.get("homepage")),
        "tel": infocenter or _clean(common.get("tel")),
        "parking": " · ".join(x for x in (parking, fee and f"주차요금 {fee}") if x) or None,
        **picked,
    }
