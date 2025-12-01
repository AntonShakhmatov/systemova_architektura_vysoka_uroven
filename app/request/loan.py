from app.request.validator import validate_loan_request


class LoanManager:
    def __init__(self):
        self.loans = {}

    def _get_request_for_loan(self, user_id: int, name, lastname, birthdate, rodne_cislo, phone, email, address, type_of_employment, monthly_income, amount, term, status) -> dict:
        # This is a placeholder for actual implementation
        return {"user_id": user_id, "name": name, "lastname": lastname, "birthdate":birthdate, "rodne_cislo": rodne_cislo, "phone": phone, "email": email, "amount": amount, "address": address, "type_of_employment": type_of_employment, "monthly_income": monthly_income, "term": term, status: "active"}
    
    def create_loan_request(
        self, user_id: int, name, lastname, birthdate, rodne_cislo, phone,
        email, address, type_of_employment, monthly_income, amount, term
    ) -> dict:
        
        # 1. validace údajů žadatele
        self.validator.validate_loan_request(
            user_id, name, lastname, birthdate, rodne_cislo, phone,
            email, address, type_of_employment, monthly_income, amount, term
        )

        # 2. dovoluji vytvořit žádost o úvěr
        loan_request = self._get_request_for_loan(
            user_id, name, lastname, birthdate, rodne_cislo, phone, email,
            address, type_of_employment, monthly_income, amount, term,
            status="pending"
        )

        return loan_request
    
