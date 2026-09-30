import psycopg
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.db import connect
from app.models import Health
from app.routers import regions, stats

app = FastAPI(
    title="숨은여행지도 API",
    description="관광빅데이터로 사람들이 덜 가는 곳을 찾는 API. 데이터 출처: 한국관광공사, SGIS",
    version="0.1.0",
)
# 읽기 전용 공개 API 라 어느 화면(Vercel 등)에서든 부를 수 있게 둔다
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["GET"])


# DB 접속 오류를 흔한 원인별로 알려 준다. 오류 원문에는 접속 주소가 섞일 수 있어 그대로 돌려주지 않는다.
DB_ERROR_HINTS = [
    ("password authentication failed", "비밀번호가 맞지 않습니다"),
    ("tenant or user not found", "사용자명(postgres.프로젝트ref)이 맞지 않습니다"),
    ("could not translate host name", "호스트 주소를 찾을 수 없습니다"),
    ("nodename nor servname", "호스트 주소를 찾을 수 없습니다"),
    ("network is unreachable", "네트워크에 닿지 않습니다 (Supabase Session pooler 주소를 쓰세요)"),
    ("timeout", "접속 시간이 초과됐습니다"),
    ("invalid dsn", "DATABASE_URL 형식이 잘못됐습니다 (따옴표·공백·'DATABASE_URL=' 이 들어갔는지 확인)"),
    ("invalid connection option", "DATABASE_URL 형식이 잘못됐습니다"),
    ("invalid integer value", "DATABASE_URL 의 포트가 잘못됐습니다"),
]


def _db_error_hint(e: psycopg.Error) -> str:
    msg = str(e).lower()
    for key, hint in DB_ERROR_HINTS:
        if key in msg:
            return f"{type(e).__name__}: {hint}"
    return type(e).__name__


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
        return JSONResponse(status_code=503, content={"status": "error", "db": _db_error_hint(e)})
    return {"status": "ok", "db": "ok"}


app.include_router(regions.router)
app.include_router(stats.router)
