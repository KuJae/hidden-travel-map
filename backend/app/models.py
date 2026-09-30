from datetime import date

from pydantic import BaseModel, Field


class Health(BaseModel):
    status: str = Field(examples=["ok"])
    db: str = Field(description="DB 연결 상태", examples=["ok"])


class RegionSummary(BaseModel):
    code: str = Field(description="관광빅데이터 시군구 코드", examples=["11110"])
    sido_nm: str = Field(examples=["서울특별시"])
    signgu_nm: str = Field(examples=["종로구"])
    sgis_code: str | None = Field(
        description="SGIS 2025 경계 코드. 일반구가 있는 시와 2026 개편 지역(인천 신설 구)은 없음", examples=["11010"],
    )
    window_start: date | None = Field(description="집계 시작일")
    window_end: date | None = Field(description="집계 기준일 (최신 공개일)")
    avg_daily_visitors: float | None = Field(description="외지인 + 외국인 일평균 방문자 수")
    percentile: float | None = Field(description="전국 방문량 백분위 0~100. 작을수록 덜 방문 ('하위 N%')")
    ghost_index: float | None = Field(description="100 - percentile. 팀이 정의한 탐색용 지표")
    attraction_count: int = Field(description="사진 있는 관광지 수")
    is_candidate: bool = Field(description="숨은 지역 후보 여부 (방문량 하위 30% 이면서 사진 있는 관광지 3곳 이상)")


class VisitorMix(BaseModel):
    visitor_type: int = Field(description="1 현지인, 2 외지인, 3 외국인")
    label: str
    daily_avg: float = Field(description="시 단위 전체 합의 일평균")
    share: float = Field(description="비중 (%)")


class RegionShare(BaseModel):
    sido_nm: str
    signgu_nm: str
    local_share: float = Field(description="현지인 비중 (%)")


class StatsOverview(BaseModel):
    window_start: date
    window_end: date = Field(description="집계 기준일 (최신 공개일)")
    days: int
    region_count: int = Field(description="시 단위 지역 수")
    subregion_count: int = Field(description="상위 시로 모은 일반구 수")
    attraction_count: int = Field(description="사진 있는 관광지 수")
    visitor_rows: int = Field(description="visitor_daily 저장 행 수")
    visitor_mix: list[VisitorMix]
    local_share_lowest: list[RegionShare] = Field(description="현지인 비중이 가장 낮은 곳")
    local_share_highest: list[RegionShare] = Field(description="현지인 비중이 가장 높은 곳")
    median_daily_visitors: float
    hidden_max_percentile: int = Field(description="숨은 지역 후보 기준: 방문량 하위 몇 % (팀 기준 30)")
    hidden_min_attractions: int = Field(description="숨은 지역 후보 기준: 사진 있는 관광지 최소 개수 (팀 기준 3)")
    threshold_hidden: float = Field(description="기준 백분위에 해당하는 방문량 경계 (외지인+외국인 일평균)")
    hidden_count: int = Field(description="숨은 지역 후보 수")
    hidden_gun_count: int = Field(description="숨은 지역 후보 중 이름이 '군'으로 끝나는 지역 수")
    hidden_p20: int = Field(description="비교용: 기준을 하위 20% 로 좁혔을 때의 후보 수")
    corr_log_attractions_visitors: float = Field(
        description="ln(사진 있는 관광지 수) 와 ln(일평균 방문량) 의 피어슨 상관계수. 0 에 가까우면 볼거리와 방문량이 무관")
    median_attractions_bottom20: float = Field(description="방문량 하위 20% 지역의 사진 있는 관광지 수 중앙값")
    median_attractions_all: float
    median_attractions_top20: float = Field(description="방문량 상위 20% 지역의 사진 있는 관광지 수 중앙값")


class SidoStats(BaseModel):
    sido_nm: str
    region_count: int
    median_daily_visitors: float = Field(description="시군구 일평균(외지인+외국인)의 중앙값")
    local_share: float = Field(description="현지인 비중 (%)")
    outsider_share: float = Field(description="외지인 비중 (%)")
    foreigner_share: float = Field(description="외국인 비중 (%)")
    hidden_count: int = Field(description="숨은 지역 후보 수 (하위 30%, 사진 3곳 이상)")
    attraction_count: int


class Attraction(BaseModel):
    content_id: str = Field(description="TourAPI contentid")
    title: str
    category: str | None = Field(description="관광지 / 문화시설 / 레포츠")
    address: str | None
    lat: float | None
    lon: float | None
    image_url: str = Field(description="TourAPI 대표 이미지 URL")
    image_license: str | None = Field(
        description="공공누리 유형. Type1 출처표시, Type3 출처표시+변경금지 (화면에 '출처: 한국관광공사' 표시)",
        examples=["Type3"],
    )
