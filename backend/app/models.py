from datetime import date

from pydantic import BaseModel, Field


class Health(BaseModel):
    status: str = Field(examples=["ok"])
    db: str = Field(description="DB 연결 상태", examples=["ok"])


class RegionSummary(BaseModel):
    code: str = Field(description="관광빅데이터 시군구 코드", examples=["11110"])
    sido_nm: str = Field(examples=["서울특별시"])
    signgu_nm: str = Field(examples=["종로구"])
    sgis_code: str | None = Field(description="SGIS 경계 코드 (지도 GeoJSON 과 연결)", examples=["11010"])
    window_start: date | None = Field(description="집계 시작일")
    window_end: date | None = Field(description="집계 기준일 (최신 공개일)")
    avg_daily_visitors: float | None = Field(description="외지인 + 외국인 일평균 방문자 수")
    percentile: float | None = Field(description="전국 방문량 백분위 0~100. 작을수록 덜 방문 ('하위 N%')")
    ghost_index: float | None = Field(description="100 - percentile. 팀이 정의한 탐색용 지표")
    attraction_count: int = Field(description="사진 있는 관광지 수")


class Attraction(BaseModel):
    content_id: str = Field(description="TourAPI contentid")
    title: str
    category: str | None = Field(description="관광지 / 문화시설 / 레포츠")
    address: str | None
    lat: float | None
    lon: float | None
    image_url: str = Field(description="TourAPI 대표 이미지 URL")
