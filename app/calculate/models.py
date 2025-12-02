# app/calculate/models.py
from enum import Enum
from pydantic import BaseModel, Field
from typing import List
from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import declarative_base

class EmploymentType(str, Enum):
    full_time = "full-time"
    part_time = "part-time"
    self_employed = "self-employed"
    unemployed = "unemployed"
    student = "student"


class ScoringRequest(BaseModel):
    age: int = Field(..., ge=18, le=100)
    monthly_income: float = Field(..., ge=0)
    total_monthly_installment: float = Field(..., ge=0)
    active_loans_count: int = Field(..., ge=0)
    loan_history_years: int = Field(..., ge=0)
    current_arrears_days: int = Field(..., ge=0)
    max_arrears_last_12m: int = Field(..., ge=0)
    had_past_due_payments: bool
    employment_type: EmploymentType

    term: int 
    loan_amount: float


class ScoreResponse(BaseModel):
    loan_score: float
    risk_level: str
    reason: List[str]


Base = declarative_base()


class LoanScore(Base):
    __tablename__ = "scoring_response"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    loan_score = Column(Integer, nullable=False)
    risk_level = Column(String, nullable=False)
    reason = Column(Text)