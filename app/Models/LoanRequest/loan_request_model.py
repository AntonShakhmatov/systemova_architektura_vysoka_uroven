# app/Models/LoanRequest/loan_request_model.py
from pydantic import BaseModel
from sqlalchemy import Column, Integer, DateTime, func
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class RequestResponse(BaseModel):
    name: str
    lastname: str
    birthdate: str
    monthly_income_str: float
    employment_type_str: str
    total_monthly_installment: float

class InsertRequest(Base):
    __tablename__ = "loan_request_ids"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    created_at = Column(DateTime, server_default=func.now())
