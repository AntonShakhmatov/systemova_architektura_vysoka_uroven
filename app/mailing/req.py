# app/mailing/req.py
from __future__ import annotations
import time
from typing import Optional, List, Dict

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError, OperationalError
from database.database_connector import get_engine

from api_registr.req import (
    fetch_all_user_ids,
    fetch_default_name,
    fetch_default_lastname,
    fetch_default_birthdate,
    fetch_rodne_cislo,
    fetch_default_employment_place,
    fetch_default_employment_type,
    fetch_default_monthly_income,
    fetch_default_loan_amount,
    fetch_default_term,
    fetch_default_total_monthly_installment
)


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


def fetch_default_loan_score_from_scoring_response(uid: int) -> str:
    return _fetch_single_value(
        """
        SELECT loan_score
        FROM scoring_response
        WHERE user_id = :uid
        ORDER BY created_at DESC
        LIMIT 1
        """,
        {"uid": uid},
    )


def fetch_default_risk_level_from_scoring_response(uid: int) -> str:
    return _fetch_single_value(
        """
        SELECT risk_level
        FROM scoring_response
        WHERE user_id = :uid
        ORDER BY created_at DESC
        LIMIT 1
        """,
        {"uid": uid},
    )


def fetch_default_reason_from_scoring_response(uid: int) -> str:
    return _fetch_single_value(
        """
        SELECT reason
        FROM scoring_response
        WHERE user_id = :uid
        ORDER BY created_at DESC
        LIMIT 1
        """,
        {"uid": uid},
    )


def fetch_user_profiles() -> List[Dict]:
    user_ids = fetch_all_user_ids()
    result = []

    for uid in user_ids:
        profile = {
            "user_id": uid,
            "name": fetch_default_name(uid),
            "lastname": fetch_default_lastname(uid),
            "birthdate": fetch_default_birthdate(uid),
            "rodne_cislo": fetch_rodne_cislo(uid),
            "employment_place": fetch_default_employment_place(uid),
            "employment_type": fetch_default_employment_type(uid),
            "monthly_income": fetch_default_monthly_income(uid),
            "loan_amount": fetch_default_loan_amount(uid),
            "term": fetch_default_term(uid),
            "total_monthly_installment": fetch_default_total_monthly_installment(uid),
            "loan_score": fetch_default_loan_score_from_scoring_response(uid),
            "risk_level": fetch_default_risk_level_from_scoring_response(uid),
            "reason": fetch_default_reason_from_scoring_response(uid),
        }
        result.append(profile)

    return result
