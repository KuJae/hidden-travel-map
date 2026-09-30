# 숨은여행지도 — 1조 프로젝트 맥락

## 0. 수업 공식 요구사항 (교수님 안내 자료 기준, 이강훈 기획안보다 우선)

### 일정
- 5주차(추석 연휴 이후): 예정 강의 + 기초 개념 퀴즈(객관식 실시간 스피드 퀴즈) + 팀 과제 아이디어 공유
  - 발표 2~3분, 자료는 슬라이드 1~2장 또는 웹페이지
  - 공유 내용: 진행하고 싶은 주제, 해결하려는 문제, 구현하고 싶은 주요 기능, 현재 아이디어와 방향
  - 발표 전까지 팀별 페이지 제작 (= docs/ 팀 페이지)
- 8주차: 팀별 프로젝트 발표
  - 강의계획서: **발표는 별도 슬라이드 없이 팀 프로젝트 페이지에 통합 정리해 진행**한다. 아래 링크 3개·문서 2개·필수 내용도 결국 docs/ 팀 페이지에 들어가야 한다.
  - 강의계획서: 매주 수업 마지막 팀 시간에 실습 기록을 쓰고, 그 주에 확정한 항목을 팀 페이지에 반영한다.
- 주차별 수업: 6주차 공공 Open API(인증키·Pagination·파싱·저장 수집기), 7주차 OpenSearch 검색과 AWS

### 개발 환경과 배포 (수업에서 배운 환경 사용)
- 프론트엔드: React 기본 (HTML·CSS·JavaScript 직접 구현도 가능) → Vercel
- 백엔드: FastAPI → Render
- DB: PostgreSQL → Supabase
- 소스 코드: GitHub 저장소

### 데이터 수집·활용
- 외부 API 연동(오픈 데이터·텍스트 데이터) 또는 크롤링 등으로 비정형 데이터 수집
- 출처 명시: API·오픈 데이터의 명칭, 제공 기관, 출처 URL (크롤링 시 대상 사이트와 수집 항목)
- 필수 페이지: 수집한 데이터에 대한 설명과 기초 분석·정리 결과를 보여주는 페이지

### 8주차 발표 필수 내용
1. 서비스 아키텍처: 프론트엔드·백엔드·DB·외부 API 구성, 연결 관계, 데이터 흐름
2. 사용 데이터 및 출처: 명칭, 제공 기관, 출처 URL
3. 데이터 활용 기획 시나리오: 어떤 사용자의 어떤 문제를 해결하고, 데이터를 어떻게 활용하는지
4. 비즈니스 모델: 대상 고객, 제공 가치, 수익 창출 또는 지속 가능한 운영 방안
5. 주요 페이지 및 기능: 구현했거나 구현할 예정인 페이지 구성과 기능
6. 데이터 분석·정리 결과: 분석 페이지와 주요 결과

### 발표 자료에 넣을 링크 3개
- GitHub 저장소 주소
- 서비스 웹 주소 (Vercel에 배포한 프론트엔드)
- Swagger UI 주소 (Render에 배포한 FastAPI의 /docs)

### 발표 자료에 넣을 문서 2개
- API 설명 문서: 주요 API의 기능, 요청 방식, 입력값, 응답 형식
- DB 테이블 문서: 테이블 구성, 주요 컬럼, 기본키·외래키, 테이블 간 관계

### 평가
- 에이전트 코딩 활용 가능
- 프론트엔드는 평가에서 제외. 발표에서는 기획, 구조, 데이터 활용 방식, 주요 기능을 설명
- 우선순위: 데이터 수집·DB·FastAPI·데이터 분석 페이지·문서 > 화면 꾸미기

### 기획안 대비 추가로 챙겨야 할 것 (미정, 팀 논의 필요)
- 데이터 분석·정리 페이지: 기획안에 없음. 후보는 시도별 방문량 비교, 외지인·외국인 비중, 방문량과 Ghost Index 분포, 사진 있는 관광지 수와 방문량의 관계
- 비즈니스 모델: 기획안에 없음
- 데이터 활용 시나리오: 대상 사용자와 문제를 구체화해야 함
- DB 문서용 기본키·외래키와 테이블 관계 정의
- API 문서용 입력값·응답 형식 정의 (FastAPI Pydantic 응답 모델로 정의하면 Swagger에 자동 반영)
- 5주차 팀 페이지(GitHub Pages)와 8주차 서비스 웹 주소(Vercel)는 별개

### 데이터 출처 URL
- 한국관광공사_빅데이터_지역별 방문자수_GW (기존 명칭: 관광빅데이터 정보서비스), 한국관광공사: https://www.data.go.kr/data/15101972/openapi.do
- 한국관광공사_국문 관광정보 서비스_GW (TourAPI), 한국관광공사: https://www.data.go.kr/data/15101578/openapi.do
- SGIS 행정구역경계 API (통계지리정보서비스): https://sgis.mods.go.kr (정확한 API 문서 페이지 URL은 확인 후 기입)
- 참고: 한국관광 데이터랩 https://datalab.visitkorea.or.kr

## 1. 과제와 팀
- 과목: KAIST 디지털금융 MBA 클라우드컴퓨팅실습 (BAF.60081). 수업 스택은 FastAPI, PostgreSQL, AWS 등이며, 외부 API를 연동한 백엔드+프론트엔드를 구현하는 팀 과제다.
- 1조: 이강훈, 강재구, 구대로, 박주원, 이재원 (5명)
- 주제: 이강훈 님이 기획한 「숨은여행지도」 (기획안 PDF: 숨은여행지도_팀프로젝트_구체화안_팀공유용_목업포함)
- 현재 과제: 아이디어 피칭 발표용 "팀 페이지 URL" 제출. 방향은 간단하게, 팀 소개 중심.
- 최종 목표: 8주차 발표에서 배포된 서비스로 1분 라이브 데모

## 2. 서비스 개요
- 한 줄 소개: 관광빅데이터로 '사람들이 덜 가는 곳'을 먼저 찾아주는 역발상 여행 서비스
- 핵심 메시지: "사람은 적게 가지만, 볼 것은 있다"
- 사용 흐름
  1. 전국 지도: 시군구별 방문량을 코로플레스 지도로 표시 (많이 방문 = 진하게, 적게 = 연하게)
  2. 숨은 지역 발견: 연한 지역 클릭 → 30일 일평균 방문량, 전국 방문량 하위 X% 표시
  3. 사진으로 반전: 같은 화면에 TourAPI 관광지 사진 3~6개
  4. 검색으로 좁히기 (여유 시): 계곡, 사찰, 박물관, 바다 같은 키워드 검색. 7주차 수업의 OpenSearch 활용
- 구현 원칙: 처음부터 전국을 만들지 않는다. "서울 종로구 1곳"으로 수집 → DB 저장 → FastAPI 조회 → 지도/사진 표시까지 끝까지 성공한 뒤 전국으로 확대

## 3. 외부 데이터 3종
① 관광빅데이터 (공공데이터포털 「한국관광공사_관광빅데이터 정보서비스_GW」)
  - 오퍼레이션: 기초 지자체 지역방문자수 집계 데이터 정보 조회
  - 경로: /B551011/DataLabService/locgoRegnVisitrDDList
  - 필수 파라미터: serviceKey, MobileOS, MobileApp, startYmd, endYmd (+ _type=json)
  - 응답: signguCode, signguNm, touDivCd(1 현지인, 2 외지인, 3 외국인), touNum, baseYmd
  - 기본안: 외지인(2) + 외국인(3)만 합산. 현지인은 거주자의 일상 이동이 섞이기 때문
② TourAPI (공공데이터포털 「한국관광공사_국문 관광정보 서비스_GW」, KorService2, 개발단계 자동승인·무료)
  - 지역기반 목록(areaBasedList2)으로 수집. 저장 필드: contentId, title, 주소, 위도/경도, 관광유형, 대표이미지 URL
  - 사진 없는 콘텐츠는 주요 카드에서 제외. 프론트에서 TourAPI를 직접 호출하지 않고 DB 저장 후 우리 FastAPI로 제공
③ SGIS 행정구역경계 (hadmarea.geojson)
  - Service ID/Secret Key로 accessToken 발급 → 시군구 Polygon을 GeoJSON으로 받음
  - 매일 바뀌지 않으므로 시작 시 한 번 받아 korea_sigungu.geojson 같은 정적 파일로 저장
- 보안: TOUR_API_KEY, DATA_LAB_KEY, SGIS_KEY 등은 .env에만 저장. .gitignore에 이미 포함됨. 저장소는 Public이라 절대 커밋 금지

## 4. 실제 API 동작 확인 결과 (기획안에 없는 주의사항)
- 관광빅데이터 locgoRegnVisitrDDList에는 시군구 필터 파라미터가 없다. 전국 시군구가 한 번에 내려온다 (하루 약 807행 = 269개 시군구 × 관광객 구분 3종). 종로구만 필요해도 전국 응답을 받아 걸러야 하고, 전국 확대는 날짜 루프만 돌리면 된다. 페이지네이션 필요.
- 응답 필드명은 signguCd가 아니라 signguCode. touNum은 소수점이 있는 문자열(예: '35454.599999999984')이라 NUMERIC으로 저장한다 (정수 변환하면 오류).
- [2026-09-30 실호출 확인] 최신 공개일 2026-08-31, 하루 807행 = 269개 × 3. 종로구 signguCode = 11110.
- [실호출 확인] 2026년 행정구역 개편이 반영돼 있다. 광주·전남은 앞자리 12로 통합(27개: 광주 구 12210~12330 + 전남 시군), 인천은 제물포구 28125·영종구 28155·서해구 28275·검단구 28290. 강원 51, 전북 52, 제주 50. SGIS 경계·TourAPI 법정동 코드가 이 개편을 반영했는지 반드시 확인할 것.
- [실호출 확인] 시와 그 일반구가 함께 들어 있다 (예: 수원시 41110 + 장안구 41111·권선구 41113…). 그대로 순위를 매기면 이중 계산이다.
  → **결정(2026-09-30, 강재구): 시 단위로 한다.** region_master 에는 일반구를 넣지 않고 상위 시만 넣는다
  (관광빅데이터 signguNm 이 "수원시 장안구"처럼 공백이 있으면 일반구). SGIS 경계는 일반구 단위로 오므로 시 단위로 합쳐야(dissolve) 한다. 팀에 공유할 것.
- [실호출 확인] 가끔 옛 코드 행이 섞인다 (8/4 인천 서구 28260 외국인 1행). region_master 기준으로 저장하므로 자동 제외된다.
- [실호출 확인] TourAPI: 종로구 lDongRegnCd=11, lDongSignguCd=110. 응답 필드는 소문자(contentid, sigungucode, cpyrhtDivCd…). 종로구 첫 100건 중 옛 areacode/sigungucode 빈 값 54건. 서울 관광지·문화시설·레포츠 중 종로구 사진 있는 곳 297곳.
- [실호출 확인] TourAPI 사진은 공공누리 Type1(출처표시) 또는 Type3(출처표시+변경금지) → 화면에 "출처: 한국관광공사" 표시, 사진 변형 주의. attractions.image_license 에 저장. 이미지 URL 일부가 http:// 라 https 로 바꿔 저장한다.
- [실호출 확인] SGIS: 종로구 adm_cd 11010, 좌표 UTM-K(EPSG:5179) 확인. 경계 최신 연도는 2025 (2026 요청 시 errCd -200).
  2025 경계의 인천(SGIS 23)은 옛 체계 10개(중구·동구·서구…)라 관광빅데이터 새 체계 11개(제물포구·영종구·서해구·검단구…)와 1:1이 아니다 → 인천은 경계 합치기나 근사 매핑 필요.
  광주(SGIS 24, 5개)·전남(SGIS 36, 22개)은 관광빅데이터 12xxx 와 이름이 1:1 대응한다.
- [실호출 확인] Supabase 새 프로젝트 기본값은 Data API 켜짐 + 새 테이블 자동 공개 + RLS 꺼짐이라 anon 키로 테이블 읽기·쓰기가 가능했다.
  db/schema.sql 에서 RLS 를 켜고 anon·authenticated 권한을 회수한다. postgres 계정은 BYPASSRLS 라 FastAPI·수집기에는 영향 없음.
- Supabase Session pooler 호스트는 aws-0-ap-northeast-2.pooler.supabase.com:5432, 사용자명은 postgres.<프로젝트 ref>.
- apis.data.go.kr 연결이 가끔 30초 넘게 끊긴다. 수집기는 3번까지 재시도하고, 오류 메시지에 인증키가 든 URL이 찍히지 않게 했다.
- 공개 지연이 약 1개월 (예: 9/10 기준 8/11 데이터까지만 존재). 화면 문구는 "최근 30일" 대신 "최신 공개 기준 30일"로 쓰고 기준일을 표시할 것.
- 방문자 수는 일자별 순방문자 기준 (2박 3일 체류 = 3명). 기초·광역 데이터는 집계 기준이 달라 임의 합산 불가.
- TourAPI가 법정동 코드 체계로 이관되어 기존 areaCode/sigunguCode가 빈 콘텐츠가 많다 (강원 표본 64%, 제주 58.6% 누락 사례). 호출은 resultCode=0000으로 정상 응답해 조용히 누락된다. 반드시 lDongRegnCd / lDongSignguCd로 조회할 것.
- SGIS 코드와 행안부·법정동 코드가 다르다 (예: 대전 서구 SGIS sgg_cd 25030, 법정동 30170). 관광빅데이터의 269개 시군구에는 일반구가 포함된 것으로 보여, 경계 파일 단위(예: 수원시 vs 장안구)도 맞춰야 한다. region_master가 핵심 작업이다.
- SGIS 경계 좌표가 UTM-K(EPSG:5179)로 올 가능성이 높다. Leaflet은 WGS84(EPSG:4326) 전제이므로 샘플 호출로 확인 후, 정적 파일 저장 시 geopandas to_crs(4326)로 변환하고 도형을 단순화해 용량을 줄일 것.
- 공공데이터포털 개발계정은 API마다 하루 1,000건 제한. 인증키는 계정당 하나라 관광빅데이터·TourAPI에 같은 키를 쓴다.
- SGIS API 도메인은 sgisapi.mods.go.kr (옛 sgisapi.kostat.go.kr 은 302 리다이렉트). 경계 응답 좌표계는 문서상 UTM-K(EPSG:5179).
- Render → Supabase 연결은 Session pooler 주소를 쓴다 (직접 연결 주소는 IPv6 전용).
- Render·Supabase 무료 플랜은 미사용 시 잠들거나 일시정지될 수 있다. 발표 직전 /health 호출로 깨워둘 것.
- Ghost Index는 절대 방문량 백분위라 인구·면적이 작은 군이 구조적으로 상위에 온다. "관광 가치 평가가 아닌 탐색용 지표"로 설명할 것.
- **결정(2026-09-30, 강재구): 숨은 지역 후보 = 방문량 하위 30% AND 사진 있는 관광지 3곳 이상** (기획안 본문 20% / 목업 30% 중 30%). 후보 69곳(20%였으면 46곳).
  기준값은 backend/app/rules.py 한 곳에만 있고, API 가 지역마다 is_candidate 를 내려 준다. 화면은 이 값만 쓴다.
  팀 페이지(docs/index.html)의 "하위 20%" 문구는 아직 그대로다 (팀 페이지는 요청 시에만 고친다).

## 5. 아키텍처와 백엔드 설계 (기획안 기준)
- 흐름: 외부 API(관광공사, SGIS) → 수집기(Python) → DB(PostgreSQL/Supabase) → 우리 API(FastAPI) → 화면(React, Leaflet)
- DB 테이블 4개
  - region_master: 내부 region_id, 시도/시군구명, 관광빅데이터 코드, TourAPI 코드, SGIS 코드
  - visitor_daily: region_id, date, visitor_type, visitor_count (같은 요청을 다시 해도 중복 저장되지 않게 키 설정)
  - visitor_summary: 최근 30일 일평균 방문량, 방문량 백분위, Ghost Index
  - attractions: content_id, region_id, title, category, address, lat, lon, image_url
- 계산: 일별 방문량 = 외지인 + 외국인 → 30일 평균 → 전국 백분위 → Ghost Index = 100 − 방문량 백분위 → 후보 = 방문량 하위 30% AND 사진 있는 관광지 3곳 이상 (기획안은 20%, 2026-09-30 30%로 결정). Ghost Index는 팀이 정의한 지표이며 관광공사 공식 지표가 아님
- FastAPI 엔드포인트 (/docs Swagger에서 테스트)
  - GET /health: 서버·DB 연결 확인
  - GET /regions: 전국 시군구 avg_daily_visitors, percentile, ghost_index → 지도 색칠
  - GET /regions/{code}: 선택 지역 방문량 요약
  - GET /regions/{code}/attractions: 선택 지역의 사진 있는 관광지 목록
  - GET /hidden: 숨은 지역 후보 목록
- 구현 순서: API 키 발급·샘플 호출 확인 → 종로구 1곳 End-to-End → DB 저장 → FastAPI → 전국 확대(region_master 기준, 페이지네이션, 누락·오류 로그) → GeoJSON 코드와 /regions Join해 지도 색칠, 클릭 시 상세 API → 사진 카드 → 배포
- 배포: 프론트 Vercel, 백엔드 Render, DB Supabase
- 역할(기획안): PM/서비스기획, 방문자 데이터, 관광지 데이터, 백엔드/DB, 프론트엔드/지도. 누가 무엇을 맡을지는 아직 정해지지 않았다. 팀 페이지에는 역할을 표시하지 않기로 했다.

## 6. 일정과 범위
- 5주차: API 키 발급, 3종 샘플 호출, 종로구 1곳 End-to-End, region_master 초안, Git·역할 확정
- 6주차: 전국 방문자 수집 → DB → 30일 집계·Ghost Index → 관광지·사진 저장 → FastAPI 핵심 엔드포인트
- 7주차: 코로플레스 지도, 지역 상세·사진 카드, Vercel/Render/Supabase 배포, 전체 시나리오 테스트·오류 수정
- 8주차: 기능 동결, 팀 프로젝트 페이지 정리, 1분 라이브 데모 반복, 실패 대비 캡처·샘플 응답 준비
- 제외 범위: AI 추천, 날씨, 맛집, 숙박, 여행 코스, 개인화
- 발표 완료 기준: 배포 URL에서 전국 지도 표시 / 색 농도가 실제 DB 방문량과 연결 / 연한 지역 클릭 시 "하위 X%" 표시 / 사진 있는 관광지 3곳 이상 / /docs에서 핵심 API 정상 응답 / 팀원 누구나 전체 흐름 설명 가능 / 캡처·샘플 응답 준비

## 7. 저장소 구조와 팀 페이지 (docs/index.html)
```
hidden-travel-map/
  README.md        팀용 수정·배포·개발 시작 안내
  .gitignore       .env, __pycache__, .venv, node_modules, collector/data/raw/ 등
  .env.example     필요한 키 목록 (DATA_LAB_KEY, TOUR_API_KEY, SGIS_SERVICE_ID, SGIS_SECRET_KEY, DATABASE_URL)
  render.yaml      Render Blueprint (rootDir: backend)
  db/schema.sql    테이블 4개 + 종로구 시드. 여러 번 실행해도 안전
  db/region_master.csv  전국 시군구 코드 연결표 (regions.py 출력, 검토·문서용)
  collector/       common.py(호출·페이지네이션·재시도·DB), sample_calls.py, regions.py, visitors.py, attractions.py
  backend/app/     FastAPI (main.py, db.py, models.py, routers/regions.py)
  docs/            팀 페이지 (GitHub Pages: main 브랜치 /docs)
    index.html
    images/        mockup-01-map.webp, mockup-02-detail.webp, mockup-03-theme.webp (기획안 목업 3장)
```
- 수집기는 region_master 에 등록된 지역만 저장한다. 전국 확대 = region_master 매핑을 채우는 일.
- region_master (collector/regions.py): 관광빅데이터 269개 전부. 일반구 39개는 parent_region_id 로 상위 시를 가리키고,
  순위(visitor_summary)·API 는 시 단위 230개(parent 없음)만 쓴다. 일반구 관광지는 상위 시로 모아 저장한다.
  관광빅데이터 signguCode = TourAPI lDongRegnCd + lDongSignguCd (세종만 lDongRegnCd 가 36110). SGIS 는 (시도, 이름) 매칭으로 249개 연결.
  시 단위 중 SGIS 경계가 없는 곳은 인천 제물포구·영종구·서해구·검단구 4곳 (2026 개편, 7주차 지도 때 처리).
- API: GET /health, /regions(전국 시 단위), /regions/{code}, /regions/{code}/attractions, /hidden?max_percentile=20&min_attractions=3
- [전국 수집 결과, 2026-08-02~08-31] visitor_daily 24,208행, 시 단위 230곳 순위. 방문 최하위 5곳은 영양군·울릉군·장수군·양구군·의령군
  (기획안 목업 예시와 일치). 사진 있는 관광지 17,658곳, 230곳 모두 3곳 이상. 숨은 지역 후보는 하위 20% 기준 46곳, 30% 기준 69곳.
- [실호출 확인] TourAPI arrange=Q(대표 이미지 있는 것만)가 사진 없는 콘텐츠를 완전히 거르지 않는다(서울 관광지 775건 중 50건 사진 없음) → 코드에서 firstimage 로 한 번 더 거른다.
- 화면(frontend/, React·Leaflet)은 7주차에 추가한다.
- docs/index.html은 빌드 도구 없는 단일 HTML (CSS·JS 인라인). 폰트는 Google Fonts의 Hahmlet(제목), IBM Plex Sans KR(본문)
- 디자인 토큰: 배경 #EDF0EA, 패널 #FAFBF8, 글자 #15291F, 보조 #53655A, 숲색 #2F5E4A, 강조(등불) #EBAE45, 지도 단계 --l0~--l5. 다크 모드 지원(prefers-color-scheme + data-theme)
- 구성 순서: 헤더(브랜드, "KAIST 디지털금융 MBA 클라우드컴퓨팅실습 1조", 앵커 메뉴) → 히어로(제목 "사람들이 덜 가는 곳에서 새로운 여행을 발견합니다", 부제, 육각 타일 예시 지도, 후보 5곳 칩, 선택 지역 카드) → #idea 아이디어 → #how 사용 흐름 4단계 → #screens 목업 3장(클릭 시 라이트박스) → #data 흐름도·데이터 3종·Ghost Index·API 표 → #team 5명 이름만 → #plan 일정·발표에서 보여줄 것·제외 범위 → 푸터(데이터 출처)
- 지도와 카드 수치는 기획안 목업의 예시 데이터 (JS의 data 객체: 영양군 96/7곳, 양구군 94/11곳, 장수군 92/9곳, 의령군 91/8곳, 괴산군 89/13곳). 페이지에 "예시 데이터"로 표기돼 있다.
- 팀 결정 사항: 역할 분담과 결과물 설명은 페이지에서 뺐다. 팀원은 이름만 표시한다.
- claude.ai에서 만든 미리보기 버전이 따로 있지만 Git 수정 사항은 반영되지 않는다. 과제 제출은 GitHub Pages 주소로 한다.
- 저장소: https://github.com/KuJae/hidden-travel-map (Public, 소유자 KuJae) / 팀 페이지: https://kujae.github.io/hidden-travel-map/
- 서비스 화면: https://hidden-travel-map.vercel.app (index.html 지도, analysis.html 데이터 분석). Vercel 프로젝트 hidden-travel-map (KuJae 계정),
  Root Directory frontend, 빌드 없음. .vercelignore 로 frontend 만 올린다. 주소 뒤 #지역코드 로 그 지역을 연 채 시작(데모용).
  GitHub 연결됨(2026-09-30): main 에 push 하면 Vercel 이 자동 배포한다 (Render 와 같음).
- 분석 API: /stats/overview, /stats/sido. 분석 결과 핵심: 사진 있는 관광지 수와 방문량의 상관(로그) 0.06 → "볼 것은 있다"의 근거.
- API: https://hidden-travel-map-api.onrender.com (Swagger /docs). Render 무료·싱가포르·rootDir backend·main push 시 자동 배포. 환경변수 DATABASE_URL 은 Render 대시보드에만 있다.
- 진행 상태(2026-09-30): 종로구 1곳 End-to-End 완료 — 관광빅데이터 30일·TourAPI 관광지 297곳이 Supabase 에 있고, 배포된 API 가 응답한다. 다음은 6주차 전국 확대(region_master, 시 단위).

## 8. 작업 규칙
- API 키나 비밀 값은 절대 커밋하지 않는다. 커밋 전 git status로 확인한다.
- 팀원 5명이 같은 저장소를 쓰므로, 작업 전 pull, 작은 단위로 커밋, 알아보기 쉬운 커밋 메시지를 쓴다.
- 파일 삭제, 강제 push, 히스토리 변경 같은 되돌리기 어려운 작업은 실행 전에 반드시 물어본다.
- 팀 페이지 내용이나 디자인은 요청 없이 바꾸지 않는다.
