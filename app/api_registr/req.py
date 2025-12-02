# app/api_register/req.py
from __future__ import annotations
import time
from typing import Optional, List, Dict

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError, OperationalError

from database.database_connector import get_engine


def _fetch_single_value(query: str, params: dict) -> str:
    sql = text(query)

    for attempt in range(20):
        try:
            with get_engine().connect() as conn:
                row = conn.execute(sql, params).first()
                val: Optional[str] = row[0] if row else ""
                return val or ""
        except (OperationalError, SQLAlchemyError) as e:
            print(f"[warn] DB error (attempt {attempt+1}/20): {e}")
            time.sleep(1.5)

    return ""


# All user_ids who did loan requests(get from DB)
def fetch_all_user_ids() -> List[int]:
    sql = text("SELECT DISTINCT user_id FROM loan_request_ids")

    for attempt in range(20):
        try:
            with get_engine().connect() as conn:
                rows = conn.execute(sql).fetchall()
                return [row[0] for row in rows]
        except (OperationalError, SQLAlchemyError) as e:
            print(f"[warn] DB error (attempt {attempt+1}/20): {e}")
            time.sleep(1.5)

    return []


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

def fetch_rodne_cislo(user_id: int) -> str:
    return _fetch_single_value(
        "SELECT rodne_cislo FROM users WHERE user_id = :user_id",
        {"user_id": user_id}
    )

#  ALl users who did loan request
def fetch_user_profiles() -> List[Dict]:
    user_ids = fetch_all_user_ids()
    result = []

    for uid in user_ids:
        profile = {
            "user_id": uid,
            "name": fetch_default_name(uid),
            "lastname": fetch_default_lastname(uid),
            "birthdate": fetch_default_birthdate(uid),
            "rodne_cislo": fetch_rodne_cislo(uid)
        }
        result.append(profile)

    return result
