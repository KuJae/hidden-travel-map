import psycopg
from fastapi import APIRouter, Depends, HTTPException, Path

from app.db import get_conn
from app.models import AttractionDetail
from app.routers.regions import SUMMARY_SQL
from app.tour import DETAIL_COLUMNS, TourAPIError, fetch_detail, key_fingerprint

router = APIRouter(tags=["attractions"])

CONTENT_ID = Path(description="TourAPI contentid (GET /regions/{code}/attractions 의 content_id)",
                  pattern=r"^\d{1,12}$", examples=["126508"])

UPSERT_DETAIL = f"""
    INSERT INTO attraction_details (content_id, {", ".join(DETAIL_COLUMNS)}, fetched_at)
    VALUES (%s, {", ".join(["%s"] * len(DETAIL_COLUMNS))}, now())
    ON CONFLICT (content_id) DO UPDATE SET
        {", ".join(f"{c} = EXCLUDED.{c}" for c in DETAIL_COLUMNS)}, fetched_at = EXCLUDED.fetched_at
    RETURNING fetched_at
"""


@router.get("/attractions/{content_id}", response_model=AttractionDetail,
            summary="관광지 하나의 상세 (비교함용: 이용시간·쉬는날·요금·주차 + 지역 방문량)")
def get_attraction(content_id: str = CONTENT_ID, conn: psycopg.Connection = Depends(get_conn)):
    """처음 보는 관광지는 TourAPI 상세를 받아 attraction_details 에 저장하고, 다음부터는 DB 에서 준다.
    TourAPI 가 실패하면 상세 항목은 null 로 두고 기본 정보와 지역 방문량만 돌려준다."""
    row = conn.execute(f"""
        SELECT a.content_id, a.title, a.category, a.address, a.lat, a.lon, a.image_url, a.image_license,
               a.region_id, {", ".join(f"d.{c}" for c in DETAIL_COLUMNS)}, d.fetched_at AS detail_fetched_at
        FROM attractions a
        LEFT JOIN attraction_details d USING (content_id)
        WHERE a.content_id = %s
    """, (content_id,)).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail=f"{content_id} 관광지를 찾을 수 없습니다")

    if row["detail_fetched_at"] is None:
        try:
            detail = fetch_detail(content_id, row["category"])
        except TourAPIError as e:
            # Render 로그에서 확인. 인증키는 찍지 않고 지문만 남긴다 (로컬 .env 키와 같은지 비교용)
            print(f"TourAPI 상세 실패 {content_id}: {e} (키 {key_fingerprint()})")
        else:
            saved = conn.execute(UPSERT_DETAIL, (content_id, *(detail[c] for c in DETAIL_COLUMNS))).fetchone()
            conn.commit()
            row.update(detail, detail_fetched_at=saved["fetched_at"])

    row["region"] = conn.execute(SUMMARY_SQL + " AND r.region_id = %s", (row.pop("region_id"),)).fetchone()
    return row
