# 숨은여행지도

관광빅데이터로 ‘사람들이 덜 가는 곳’을 먼저 찾아주는 역발상 여행 서비스
KAIST 디지털금융 MBA 클라우드컴퓨팅실습 1조 (이강훈, 강재구, 구대로, 박주원, 이재원)

- 팀 페이지: https://kujae.github.io/hidden-travel-map/
- 저장소: https://github.com/KuJae/hidden-travel-map

## 폴더 구조

```
docs/            팀 소개 페이지 (GitHub Pages로 배포)
  index.html
  images/        목업 이미지
.gitignore       API 키(.env) 등 올리면 안 되는 파일 목록
```

앞으로 서비스 코드는 `collector/`(데이터 수집), `backend/`(FastAPI), `frontend/`(React, Leaflet) 폴더로 추가합니다.

## 팀 페이지 수정하기

1. 작업 전에 VS Code 소스 제어 탭에서 **Pull**로 최신 내용을 받습니다.
2. `docs/index.html`을 수정합니다.
3. 미리보기: VS Code 확장 **Live Server** 설치 후, `index.html`에서 우클릭 > Open with Live Server
4. 소스 제어 탭에서 변경 내용 확인 > 메시지 입력 > **Commit** > **Sync Changes**(Push)
5. 1~2분 뒤 GitHub Pages 주소에 반영됩니다.

## 배포 (GitHub Pages)

Settings > Pages > Source: Deploy from a branch > Branch: `main`, 폴더: `/docs` > Save (설정 완료)

## 약속

- API 키는 `.env` 파일에만 저장하고 절대 커밋하지 않습니다. (`.gitignore`에 포함)
- 같은 파일을 여러 명이 동시에 고치지 않도록, 수정 전에 단톡방에 한 줄 공유합니다.
