# app/Controllers/Calculate/main.py

from enum import Enum
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from typing import List

from Controllers.Calculate.req import build_scoring_request_from_user, save_score_to_db
from Models.Calculate.calculate_model import ScoringRequest, ScoreResponse, EmploymentType
from database.database_connector import get_db

app = FastAPI(title="Kredit FastAPI")


def calculate_loan_score(data: ScoringRequest) -> ScoreResponse:
    reasons: List[str] = []
    score = 500  # base score

    # 1) Debt-to-income ratio
    if data.monthly_income == 0:
        debt_ratio = 1.0
    else:
        debt_ratio = data.total_monthly_installment / data.monthly_income

    if debt_ratio < 0.3:
        score += 120
    elif debt_ratio < 0.5:
        score += 60
        reasons.append("Moderate debt burden (30-50% of income).")
    elif debt_ratio < 0.7:
        score += 0
        reasons.append("High debt burden (50–70% of income).")
    else:
        score -= 150
        reasons.append("Very high debt burden (>70% of income).")

    # 2) Age
    if 25 <= data.age <= 60:
        score += 40
    else:
        score -= 20
        reasons.append("Age outside the optimal range of 25–60 years.")

    # 3) Loan history
    if data.loan_history_years == 0:
        score -= 40
        reasons.append("No credit history.")
    elif data.loan_history_years < 2:
        score += 0
        reasons.append("Short credit history (< 2 years).")
    else:
        score += 40
        reasons.append("Sufficiently long credit history.")

    # Počet aktivních úvěrů
    if data.active_loans_count == 0:
        # no active loans
        pass
    elif data.active_loans_count <= 3:
        score += 20
    elif data.active_loans_count <= 6:
        score += 0
        reasons.append("Increased number of active loans.")
    else:
        score -= 40
        reasons.append("Too many active loans.")

    # 4) Delays: current_arrears_days, max_arrears_last_12m, had_past_due_payments
    if data.had_past_due_payments:
        score -= 60
        reasons.append("Late payments have been recorded.")

    if data.current_arrears_days > 0:
        if data.current_arrears_days <= 30:
            score -= 40
            reasons.append("Current delinquency up to 30 days.")
        elif data.current_arrears_days <= 60:
            score -= 80
            reasons.append("Current delinquency of 31–60 days.")
        else:
            score -= 150
            reasons.append("Current delinquency of more than 60 day.")

    if data.max_arrears_last_12m > 0:
        if data.max_arrears_last_12m <= 30:
            score -= 20
            reasons.append("There have been minor delinquencies in the past 12 months.")
        elif data.max_arrears_last_12m <= 60:
            score -= 60
            reasons.append("Serious delinquencies in the past 12 months.")
        else:
            score -= 100
            reasons.append("Very serious delinquencies (60+ days) in the past 12 months.")

    # 5) Type of employment (users.employment_type)
    if data.employment_type == EmploymentType.full_time:
        score += 50
    elif data.employment_type == EmploymentType.part_time:
        score += 20
    elif data.employment_type == EmploymentType.self_employed:
        score += 10
    elif data.employment_type == EmploymentType.unemployed:
        score -= 100
        reasons.append("Unemployed client.")
    elif data.employment_type == EmploymentType.student:
        score -= 50
        reasons.append("Student with potentially unstable income.")

    # 6) Term
    if data.term <= 24:
        score += 20
        reasons.append("Short loan term (<= 24 months).")
    elif data.term <= 60:
        pass
    elif data.term <= 120:
        score -= 30
        reasons.append("Long loan term (61–120 months).")
    else:
        score -= 60
        reasons.append("Very long loan term (> 120 months).")

    # Normalizing the range
    if score < 0:
        score = 0
    if score > 1000:
        score = 1000

    # Risk level
    if score >= 750:
        risk_level = "Low"
    elif score >= 550:
        risk_level = "Medium"
    else:
        risk_level = "High"

    return ScoreResponse(loan_score=score, risk_level=risk_level, reason=reasons)


@app.get("/score/{user_id}", response_model=ScoreResponse)
def score_by_user_id(
    user_id: int,
    db: Session = Depends(get_db)
):
    scoring_request = build_scoring_request_from_user(db, user_id)
    score_response = calculate_loan_score(scoring_request)
    save_score_to_db(db, user_id, score_response)
    return score_response