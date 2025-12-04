# app/Controllers/LoanRequest/req.py
from __future__ import annotations

from sqlalchemy.orm import Session

from Models.LoanRequest.loan_request_model import InsertRequest

def save_user_id_to_db(db: Session, user_id: int) -> InsertRequest:

    db_obj = InsertRequest(user_id=user_id)
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj
