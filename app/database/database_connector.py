# app/database/database_connectror.py

import os
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker, Session

DB_DSN = "mysql+pymysql://test:test@database/test?charset=utf8mb4"

engine: Engine = create_engine(DB_DSN, future=True)
def db_url() -> str:
    url = os.getenv("DATABASE_URL")
    if url:
        return url
    host = os.getenv("DB_HOST", "database")
    port = os.getenv("DB_PORT", "3306") 
    user = os.getenv("DB_USER", "test")
    pwd  = os.getenv("DB_PASS", "test")
    name = os.getenv("DB_NAME", "test")
    return f"mysql+pymysql://{user}:{pwd}@{host}:{port}/{name}"

def get_engine():
    return create_engine(db_url(), pool_pre_ping=True, future=True)


SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    future=True
)

def get_db():
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()