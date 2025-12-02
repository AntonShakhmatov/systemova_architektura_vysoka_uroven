# app/request/loan.py
from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.request.validator import Validator
from app.request.req import save_user_id_to_db
from app.database.database_connector import get_db

app = FastAPI(title="Kredit FastAPI")


class LoanRequestIn(BaseModel):
    user_id: int
    loan_amount: float
    term: int
    percent: float
    total_monthly_installment: float


class LoanManager:
    def __init__(self, validator: Validator):
        self.validator = validator

    def create_loan_request(self, payload: LoanRequestIn) -> dict:
        """
        1) Validace se provádí na základě dat uložených při signup
           + parametrů konkrétní úvěrové žádosti.
        """
        self.validator.validate_loan_request(
            user_id=payload.user_id,
            loan_amount=payload.loan_amount,
            term=payload.term,
            percent=payload.percent,
            total_monthly_installment=payload.total_monthly_installment,
        )

        loan_request = {
            "user_id": payload.user_id,
            "loan_amount": payload.loan_amount,
            "term": payload.term,
            "percent": payload.percent,
            "total_monthly_installment": payload.total_monthly_installment,
            "status": "pending",
        }

        return loan_request


loan_manager = LoanManager(Validator())


@app.post("/loan-requests")
def create_loan_request_endpoint(
    payload: LoanRequestIn,
    db: Session = Depends(get_db),
):
    """
    ČÁST 1 + ČÁST 2:
    - přijímá nové online žádosti (POST /loan-requests),
    - automaticky předzpracuje (validace vůči users + kontrola parametrů úvěru),
    - uloží user_id do loan_request_ids (agregace žádostí).
    """
    try:
        loan_request = loan_manager.create_loan_request(payload)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    aggregate_row = save_user_id_to_db(db, payload.user_id)

    return {
        "loan_request": loan_request,
        "loan_request_aggregate_id": aggregate_row.id,
        "message": "Loan request accepted, validated and aggregated.",
    }
