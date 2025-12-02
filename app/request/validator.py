# app/request/validator.py
import re
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.engine import Engine

from app.database.database_connector import get_engine


class Validator:
    def __init__(self):
        self.engine: Engine = get_engine()

    def _fetch_user_row(self, user_id: int):
        query = text("""
            SELECT name, lastname, birthdate, rodne_cislo, phone, email, address,
                   employment_type, monthly_income
            FROM users
            WHERE user_id = :user_id
        """)
        try:
            with self.engine.connect() as conn:
                result = conn.execute(query, {"user_id": user_id})
                row = result.fetchone()
                return row
        except SQLAlchemyError as e:
            print(f"Database error: {e}")
            return None

    def validate_loan_request(
        self,
        user_id: int,
        loan_amount: float,
        term: int,
        percent: float,
        total_monthly_installment: float
    ) -> bool:
        """
        Validace loan requestu, který pracuje s už existujícím uživatelem (po signup).
        """
        row = self._fetch_user_row(user_id)
        if not row:
            raise ValueError("User not found.")

        (
            name,
            lastname,
            birthdate,
            rodne_cislo,
            phone,
            email,
            db_address,
            db_employment_type,
            db_monthly_income,
        ) = row

        # --- Kontrola základních signup-dat ---
        if not name or not lastname:
            raise ValueError("User name or lastname is missing in the system.")

        if not re.fullmatch(r"\+?[1-9]\d{1,14}$", phone or ""):
            raise ValueError("Invalid phone number format in user profile.")

        if re.fullmatch(r"[^@]+@[^@]+\.[^@]+", email or "") is None:
            raise ValueError("Invalid email format in user profile.")

        # --- Kontrola parametrů úvěru ---

        if loan_amount <= 0:
            raise ValueError("Loan amount must be a positive value.")

        if term <= 0:
            raise ValueError("Term must be a positive value.")

        if percent <= 0 or percent > 100:
            raise ValueError("Percent must be in range (0, 100].")

        if total_monthly_installment <= 0:
            raise ValueError("Total monthly installment must be a positive value.")

        # Pokud v systému známe měsíční příjem, můžeme zkontrolovat DTI
        if db_monthly_income is not None:
            try:
                income = float(db_monthly_income)
            except (TypeError, ValueError):
                income = 0.0

            if income > 0 and total_monthly_installment > income * 0.7:
                # jemné business pravidlo – splátky > 70 % příjmu
                raise ValueError("Monthly installment is too high compared to income.")

        return True
