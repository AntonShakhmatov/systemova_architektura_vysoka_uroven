from __future__ import annotations
import csv
import datetime
import time
import json
from typing import Optional
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError, OperationalError
from sqlalchemy.orm import Session
from database.database_connector import get_engine
from calculate.models import ScoringRequest, EmploymentType, ScoreResponse, LoanScore

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

def _fetch_single_value_date(query: str, params: dict) -> str:
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

def _insert_single_value(query: str, params: dict) -> str:
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
    return _fetch_single_value_date(
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

# Přiklad vyvoláni 
# _fetch_single_value(
#     "SELECT name FROM users WHERE user_id = :user_id",
#     {"user_id": 1}
# )

# Insert result to DB
def save_score_to_db(db: Session, user_id: int, response: ScoreResponse):
    db_obj = LoanScore(
        user_id=user_id,
        loan_score=response.loan_score,
        risk_level=response.risk_level,
        # reason=response.reason 
        reason=json.dumps(response.reason) 
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def build_scoring_request_from_user(db: Session, user_id: int) -> ScoringRequest:
    # 1. User info
    name = fetch_default_name(user_id)
    lastname = fetch_default_lastname(user_id)
    birthdate_str = fetch_default_birthdate(user_id)  
    monthly_income_str = fetch_monthly_income(user_id)
    employment_type_str = fetch_employment_type(user_id)
    total_monthly_installment = fetch_total_monthly_installment(user_id)

    # Remake types
    birthdate = datetime.datetime.fromisoformat(str(birthdate_str))
    today = datetime.datetime.now()
    age = today.year - birthdate.year - int((today.month, today.day) < (birthdate.month, birthdate.day))

    monthly_income = float(monthly_income_str or 0)

    # 2. CSV path
    birthdate_for_filename = birthdate.strftime("%Y-%m-%d")
    csv_path = f"/app/uploads/{name}_{lastname}_{birthdate_for_filename}_loan_history.csv"


    # 3. Reading CSV
    with open(csv_path, mode="r", encoding="utf-8") as csvfile:
        data = list(csv.DictReader(csvfile))

    # active_loans_count
    active_loans_count = sum(1 for row in data if row.get("status", "").lower() == "active")

    # max_arrears_last_12m
    max_arrears_last_12m = max(
        int(row["max_arrears_last_12m"])
        for row in data
        if row.get("max_arrears_last_12m", "").strip() != ""
    )

    csv_monthly_installment = sum(
        int(row["monthly_installment"])
        for row in data
        if row.get("monthly_installment").strip() != ""
    )

    # current_arrears_days
    current_arrears_days = max(
        int(row["current_arrears_days"])
        for row in data
        if row.get("current_arrears_days", "").strip() != ""
    )

    # loan_history_years
    def calc_loan_history_years_from_csv(csv_path: str) -> int:
        with open(csv_path, mode="r", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))

        opened_dates = []
        for row in rows:
            date_str = row.get("opened_date", "").strip()
            if date_str:
                try:
                    opened_dates.append(datetime.datetime.strptime(date_str, "%Y-%m-%d").date())
                except ValueError:
                    print(f"Warning: invalid date format: {date_str}")

        if not opened_dates:
            return 0

        earliest = min(opened_dates)
        today_date = datetime.datetime.now().date()

        return (
            today_date.year
            - earliest.year
            - int((today_date.month, today_date.day) < (earliest.month, earliest.day))
        )

    loan_history_years = calc_loan_history_years_from_csv(csv_path)

    # total_monthly_installment
    # total_monthly_installment = sum(int(row["monthly_installment"]) for row in data if row["monthly_installment"].strip() != "")
    # total_monthly_installment_str = fetch_total_monthly_installment(user_id) # totoal_monthly_installment z DB
    total_monthly_installment_str = total_monthly_installment
    total_monthly_installment = float(total_monthly_installment_str or 0)

    # had_past_due_payments — если была просрочка либо сейчас, либо в прошлом
    had_past_due_payments = (max_arrears_last_12m > 0) or (current_arrears_days > 0)

    # employment_type к enum
    employment_type = EmploymentType(employment_type_str)

    # Collecting ScoringRequest
    return ScoringRequest(
        age=age,
        monthly_income=monthly_income,
        total_monthly_installment=total_monthly_installment,
        active_loans_count=active_loans_count,
        loan_history_years=loan_history_years,
        current_arrears_days=current_arrears_days,
        max_arrears_last_12m=max_arrears_last_12m,
        had_past_due_payments=had_past_due_payments,
        employment_type=employment_type,
    )


# with open('output.json', mode='w', encoding='utf-8') as jsonfile:
#     json.dump(data, jsonfile, indent=4, ensure_ascii=False)