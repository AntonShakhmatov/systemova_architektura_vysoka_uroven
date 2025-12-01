import re
from app.database.database_connector import *
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError, OperationalError
from sqlalchemy.engine import Engine


class Validator:
    def __init__(self):
        self.validator = {}

    def _get_name(self, user_id: int) -> str:
        query = text("SELECT name FROM users WHERE id = :user_id")
        try:
            with engine.connect() as conn:
                result = conn.execute(query, {"user_id": user_id})
                row = result.fetchone()
                if row:
                    return row['name']
                return ""
        except SQLAlchemyError as e:
            print(f"Database error: {e}")
            return ""   
        
    def _get_lastname(self, user_id: int) -> str:
        query = text("SELECT lastname FROM users WHERE id = :user_id")
        try:
            with engine.connect() as conn:
                result = conn.execute(query, {"user_id": user_id})
                row = result.fetchone()
                if row:
                    return row['lastname']
                return ""
        except SQLAlchemyError as e:
            print(f"Database error: {e}")
            return ""
        
    def _get_birthdate(self, user_id: int) -> str:
        query = text("SELECT birthdate FROM users WHERE id = :user_id")
        try:
            with engine.connect() as conn:
                result = conn.execute(query, {"user_id": user_id})
                row = result.fetchone()
                if row:
                    return row['birthdate']
                return ""
        except SQLAlchemyError as e:
            print(f"Database error: {e}")
            return ""

    def _get_rodne_cislo(self, user_id: int) -> str:
        query = text("SELECT rodne_cislo FROM users WHERE id = :user_id")
        try:
            with engine.connect() as conn:
                result = conn.execute(query, {"user_id": user_id})
                row = result.fetchone()
                if row:
                    return row['rodne_cislo']
                return ""
        except SQLAlchemyError as e:
            print(f"Database error: {e}")
            return "" 
    

    def validate_loan_request(self, user_id: int, name, lastname, birthdate, rodne_cislo, phone, email, address, type_of_employment, monthly_income, amount, term) -> dict:
            # Perform validation logic here
            if name != self._get_name(user_id):
                raise ValueError("Name does not match our records.")
            if lastname != self._get_lastname(user_id):
                raise ValueError("Lastname does not match our records.")
            if birthdate != self._get_birthdate(user_id):
                raise ValueError("Birthdate does not match our records.")
            if rodne_cislo != self._get_rodne_cislo(user_id):
                raise ValueError("Rodne cislo does not match our records.")
            if not re.fullmatch(r"\+?[1-9]\d{1,14}$", phone):
                raise ValueError("Invalid phone number format.")
            if address.strip() == "":
                raise ValueError("Address cannot be empty.")
            if type_of_employment not in ["employed", "self-employed", "unemployed", "student"]:
                raise ValueError("Invalid type of employment.")
            if monthly_income < 10000:
                raise ValueError("Monthly income must be at least 10,000.")
            if re.fullmatch(r"[^@]+@[^@]+\.[^@]+", email) is None:
                raise ValueError("Invalid email format.")
            if amount <= 0:
                raise ValueError("Amount must be positive values.")
            elif term <= 0:
                raise ValueError("Term must be positive values.")
            # Additional validation can be added here
            return True