# app/request/req.py
from __future__ import annotations
import time
from typing import Optional

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError, OperationalError
from sqlalchemy.orm import Session

from database.database_connector import get_engine
from request.models import InsertRequest

def _fetch_single_value(query: str, params: dict) -> str:
    sql = text(query)

    for attempt in range(20):
        try:
            with get_engine().connect() as conn:
                row = conn.execute(sql, params).first()
                val: Optional[str] = row[0] if row else ""
                return (val or "")
        except (OperationalError, SQLAlchemyError) as e:
            print(f"[warn] DB error (attempt {attempt+1}/20): {e}")
            time.sleep(1.5)

    return ""

def fetch_default_name(user_id: int) -> str:
    return _fetch_single_value(
        "SELECT name FROM users WHERE user_id = :user_id",
        {"user_id": user_id}
    )

def fetch_default_lastname(user_id: int) -> str:
    return _fetch_single_value(
        "SELECT lastname FROM users WHERE user_id = :user_id",
        {"user_id": user_id}
    )

def fetch_default_birthdate(user_id: int) -> str:
    return _fetch_single_value(
        "SELECT birthdate FROM users WHERE user_id = :user_id",
        {"user_id": user_id}
    )

def fetch_monthly_income(user_id: int) -> str:
    return _fetch_single_value(
        "SELECT monthly_income FROM users WHERE user_id = :user_id",
        {"user_id": user_id}
    )

def fetch_loan_amount(user_id: int) -> str:
    return _fetch_single_value(
        "SELECT loan_amount FROM loan_request WHERE user_id = :user_id",
        {"user_id": user_id}
    )

def fetch_total_monthly_installment(user_id: int) -> str:
    return _fetch_single_value(
        "SELECT total_monthly_installment FROM loan_request WHERE user_id = :user_id",
        {"user_id": user_id}
    )

def fetch_employment_type(user_id: int) -> str:
    return _fetch_single_value(
        "SELECT employment_type FROM users WHERE user_id = :user_id",
        {"user_id": user_id}
    )

def save_user_id_to_db(db: Session, user_id: int) -> InsertRequest:
    """
    Агрегируем заявку: просто сохраняем user_id в loan_request_ids.
    Это ровно тот момент, когда пользователь подал кредитную заявку.
    """
    db_obj = InsertRequest(user_id=user_id)
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj
