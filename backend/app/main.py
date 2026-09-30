import psycopg
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.db import connect
from app.models import Health
from app.routers import regions

app = FastAPI(
    title="숨은여행지도 API",
    description="관광빅데이터로 사람들이 덜 가는 곳을 찾는 API. 데이터 출처: 한국관광공사, SGIS",
    version="0.1.0",
)
# 읽기 전용 공개 API 라 어느 화면(Vercel 등)에서든 부를 수 있게 둔다
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["GET"])


@app.get("/", include_in_schema=False)
def read_root():
    return {"message": "숨은여행지도 API", "docs": "/docs"}


@app.get("/health", response_model=Health, summary="서버·DB 연결 확인",
         responses={503: {"model": Health, "description": "DB 연결 실패"}})
def health_check():
    try:
        with connect() as conn:
            conn.execute("SELECT 1")
    except RuntimeError as e:
        return JSONResponse(status_code=503, content={"status": "error", "db": str(e)})
    except psycopg.Error as e:
        return JSONResponse(status_code=503, content={"status": "error", "db": type(e).__name__})
    return {"status": "ok", "db": "ok"}


app.include_router(regions.router)
