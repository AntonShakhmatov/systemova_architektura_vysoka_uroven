# app/Controllers/Calculate/req.py
from __future__ import annotations
import os
import csv
import datetime
import json

from sqlalchemy.orm import Session

from database.requests import fetch_default_name, fetch_default_lastname, fetch_default_birthdate, fetch_default_monthly_income, fetch_employment_type, fetch_loan_amount, fetch_term, fetch_total_monthly_installment
from Models.Calculate.calculate_model import ScoringRequest, EmploymentType, ScoreResponse, LoanScore


# Insert result to DB
def save_score_to_db(db: Session, user_id: int, response: ScoreResponse):
    db_obj = LoanScore(
        user_id=user_id,
        loan_score=response.loan_score,
        risk_level=response.risk_level,
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
    monthly_income_str = fetch_default_monthly_income(user_id)
    employment_type_str = fetch_employment_type(user_id)

    loan_amount_str = fetch_loan_amount(user_id)
    term_str = fetch_term(user_id)
    total_monthly_installment_str = fetch_total_monthly_installment(user_id)
    birthdate = datetime.datetime.fromisoformat(str(birthdate_str))
    today = datetime.datetime.now()
    age = today.year - birthdate.year - int(
        (today.month, today.day) < (birthdate.month, birthdate.day)
    )

    monthly_income = float(monthly_income_str or 0)
    loan_amount = float(loan_amount_str or 0)
    term = int(term_str or 0)
    total_monthly_installment = float(total_monthly_installment_str or 0)

    # 2. CSV path – loan history from CSV
    birthdate_for_filename = birthdate.strftime("%Y-%m-%d")
    csv_path_new = f"/app/uploads/{user_id}_{name}_{lastname}_{birthdate_for_filename}_loan_history.csv"
    csv_path_old = f"/app/uploads/{name}_{lastname}_{birthdate_for_filename}_loan_history.csv"

    csv_path = csv_path_new if os.path.exists(csv_path_new) else csv_path_old
    if not os.path.exists(csv_path):
        raise ValueError(f"Loan history CSV not found for user_id={user_id}")

    # 3. Reading CSV
    with open(csv_path, mode="r", encoding="utf-8") as csvfile:
        data = list(csv.DictReader(csvfile))

    # active_loans_count
    active_loans_count = sum(
        1 for row in data if row.get("status", "").strip().lower() == "active"
    )

    # max_arrears_last_12m
    max_arrears_last_12m = max(
        int(row["max_arrears_last_12m"])
        for row in data
        if row.get("max_arrears_last_12m", "").strip() != ""
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
                    opened_dates.append(
                        datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
                    )
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

    had_past_due_payments = (max_arrears_last_12m > 0) or (current_arrears_days > 0)

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
        term=term,
        loan_amount=loan_amount,
    )