# 숨은여행지도

관광빅데이터로 ‘사람들이 덜 가는 곳’을 먼저 찾아주는 역발상 여행 서비스
KAIST 디지털금융 MBA 클라우드컴퓨팅실습 1조 (이강훈, 강재구, 구대로, 박주원, 이재원)

- 팀 페이지: https://kujae.github.io/hidden-travel-map/
- 저장소: https://github.com/KuJae/hidden-travel-map
- API (Swagger UI): https://hidden-travel-map-api.onrender.com/docs  — 무료 플랜이라 한동안 안 쓰면 잠들어 첫 요청이 1분쯤 걸림

## 폴더 구조

```
docs/              팀 소개 페이지 (GitHub Pages로 배포)
db/schema.sql      DB 테이블 4개 (Supabase SQL Editor에서 실행)
collector/         외부 API 수집기 (Python)
  sample_calls.py    API 3종 샘플 호출, 응답 모양 확인
  visitors.py        관광빅데이터 방문자 수 → visitor_daily, visitor_summary
  attractions.py     TourAPI 관광지·사진 → attractions
backend/           FastAPI (Render로 배포)
render.yaml        Render 배포 설정
.env.example       필요한 키 목록 (복사해서 .env로)
```

화면(`frontend/`, React·Leaflet)은 7주차에 추가합니다.

## 개발 시작하기

처음 한 번만 준비합니다. (Python 3.11 이상)

```bash
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r collector/requirements.txt -r backend/requirements.txt
cp .env.example .env               # 그다음 .env 에 키를 채운다
```

순서대로 실행합니다. 지금은 **서울 종로구 1곳**만 끝까지 연결하는 단계입니다.

1. `python collector/sample_calls.py` — 키가 제대로 동작하는지, 응답 필드가 예상과 같은지 확인
2. Supabase > SQL Editor에 `db/schema.sql` 전체를 붙여 넣고 Run — 테이블 4개와 종로구 1행 생성
3. `python collector/visitors.py` — 최신 공개일 기준 30일 방문자 수 저장 (다시 돌려도 중복 없음)
4. `python collector/attractions.py` — 종로구의 사진 있는 관광지 저장
5. `cd backend && uvicorn app.main:app --reload` — http://127.0.0.1:8000/docs 에서 API 확인

공공데이터포털 개발계정은 API마다 **하루 1,000건**까지 호출할 수 있습니다.

## 팀 페이지 수정하기

1. 작업 전에 VS Code 소스 제어 탭에서 **Pull**로 최신 내용을 받습니다.
2. `docs/index.html`을 수정합니다.
3. 미리보기: VS Code 확장 **Live Server** 설치 후, `index.html`에서 우클릭 > Open with Live Server
4. 소스 제어 탭에서 변경 내용 확인 > 메시지 입력 > **Commit** > **Sync Changes**(Push)
5. 1~2분 뒤 GitHub Pages 주소에 반영됩니다.

## 배포

- 팀 페이지 (GitHub Pages): Settings > Pages > Branch `main`, 폴더 `/docs` (설정 완료)
- API (Render): New > Blueprint > 이 저장소 선택 → `render.yaml` 설정이 채워짐 → `DATABASE_URL`에 Supabase **Session pooler** 주소 입력

## 약속

- API 키는 `.env` 파일에만 저장하고 절대 커밋하지 않습니다. (`.gitignore`에 포함)
- 같은 파일을 여러 명이 동시에 고치지 않도록, 수정 전에 단톡방에 한 줄 공유합니다.
