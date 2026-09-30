-- 숨은여행지도 DB 스키마 (Supabase PostgreSQL)
-- 사용법: Supabase > SQL Editor 에 파일 전체를 붙여 넣고 Run
-- 여러 번 실행해도 안전합니다 (IF NOT EXISTS, ON CONFLICT).
--
-- 테이블 관계
--   region_master 1 ── N visitor_daily     (region_id)
--   region_master 1 ── 1 visitor_summary   (region_id)
--   region_master 1 ── N attractions       (region_id)


-- 1) 지역 마스터: 세 데이터 출처의 서로 다른 시군구 코드를 한 행으로 잇는다.
--    수집기는 이 표에 있는 지역만 저장하므로, 전국 확대 = 이 표에 행을 채우는 일이다.
CREATE TABLE IF NOT EXISTS region_master (
    region_id        SERIAL PRIMARY KEY,
    sido_nm          TEXT NOT NULL,          -- 시도명 (예: 서울특별시)
    signgu_nm        TEXT NOT NULL,          -- 시군구명 (예: 종로구)
    datalab_code     TEXT NOT NULL UNIQUE,   -- 관광빅데이터 signguCode (예: 11110). API 경로의 {code}
    ldong_regn_cd    TEXT,                   -- TourAPI lDongRegnCd, 법정동 시도 코드 (예: 11)
    ldong_signgu_cd  TEXT,                   -- TourAPI lDongSignguCd, 법정동 시군구 코드 (예: 110)
    sgis_code        TEXT                    -- SGIS 경계 adm_cd (예: 11010). 법정동 코드와 체계가 다르다
);


-- 2) 일별 방문자 수: 관광빅데이터 locgoRegnVisitrDDList 원본을 지역·날짜·관광객 구분별로 저장
CREATE TABLE IF NOT EXISTS visitor_daily (
    region_id      INTEGER  NOT NULL REFERENCES region_master (region_id),
    base_date      DATE     NOT NULL,                                     -- baseYmd
    visitor_type   SMALLINT NOT NULL CHECK (visitor_type IN (1, 2, 3)),   -- touDivCd: 1 현지인, 2 외지인, 3 외국인
    visitor_count  NUMERIC  NOT NULL,                                     -- touNum (문자열로 와서 숫자로 변환)
    PRIMARY KEY (region_id, base_date, visitor_type)                      -- 같은 날짜를 다시 수집해도 중복되지 않는다
);


-- 3) 방문량 요약: 최신 공개일 기준 30일 평균과 전국 백분위, Ghost Index
--    collector/visitors.py 가 수집 뒤 다시 계산한다.
CREATE TABLE IF NOT EXISTS visitor_summary (
    region_id           INTEGER PRIMARY KEY REFERENCES region_master (region_id),
    window_start        DATE    NOT NULL,
    window_end          DATE    NOT NULL,     -- 기준일 (화면에 "최신 공개 기준"으로 표시)
    avg_daily_visitors  NUMERIC NOT NULL,     -- 외지인 + 외국인 일평균
    percentile          NUMERIC NOT NULL,     -- 전국 방문량 백분위 0~100 (작을수록 덜 방문)
    ghost_index         NUMERIC NOT NULL,     -- 100 - percentile (팀 정의 탐색용 지표)
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT now()
);


-- 4) 관광지: TourAPI areaBasedList2 중 대표 사진이 있는 콘텐츠
CREATE TABLE IF NOT EXISTS attractions (
    content_id  TEXT PRIMARY KEY,                                          -- contentid
    region_id   INTEGER NOT NULL REFERENCES region_master (region_id),
    title       TEXT    NOT NULL,
    category    TEXT,                                                      -- contenttypeid 이름 (관광지, 문화시설, 레포츠)
    address     TEXT,                                                      -- addr1
    lat         DOUBLE PRECISION,                                          -- mapy
    lon         DOUBLE PRECISION,                                          -- mapx
    image_url   TEXT    NOT NULL,                                          -- firstimage
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS attractions_region_idx ON attractions (region_id);


-- 시작 지역: 서울 종로구 1곳 (코드는 샘플 호출로 확인한 뒤 필요하면 고친다)
INSERT INTO region_master (sido_nm, signgu_nm, datalab_code, ldong_regn_cd, ldong_signgu_cd, sgis_code)
VALUES ('서울특별시', '종로구', '11110', '11', '110', '11010')
ON CONFLICT (datalab_code) DO NOTHING;
