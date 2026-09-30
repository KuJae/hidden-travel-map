"""DB 연결. DATABASE_URL 은 로컬에서는 저장소 루트의 .env, Render 에서는 환경변수로 받는다."""
import os
from pathlib import Path

import psycopg
from dotenv import load_dotenv
from fastapi import HTTPException
from psycopg.rows import dict_row

load_dotenv(Path(__file__).resolve().parents[2] / ".env")


def connect() -> psycopg.Connection:
    url = os.getenv("DATABASE_URL")
    if not url:
        raise RuntimeError("DATABASE_URL 이 설정되지 않았습니다")
    # prepare_threshold=None: Supabase pooler 에서 prepared statement 오류가 나지 않게 한다
    return psycopg.connect(url, row_factory=dict_row, prepare_threshold=None, connect_timeout=10)


def get_conn():
    """FastAPI 의존성: 요청마다 연결을 열고, 응답이 끝나면 닫는다."""
    try:
        conn = connect()
    except (RuntimeError, psycopg.OperationalError) as e:
        raise HTTPException(status_code=503, detail="DB 에 연결할 수 없습니다") from e
    with conn:
        yield conn
