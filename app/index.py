from app.request.loan import LoanManager
from app.api_registr.loan_history import LoanHistory
from app.calculate.main import calculate_loan_score

class Application:
    def __init__(self):
        self.loan_manager = LoanManager()
        self.registr = LoanHistory()

    def process_loan_request(self, user_id: int, name, lastname, birthdate, rodne_cislo, phone,
                               email, address, type_of_employment, monthly_income,
                               amount, term) -> dict:
        # Create a loan request using the LoanManager
        loan_request = self.loan_manager.create_loan_request(
            user_id, name, lastname, birthdate, rodne_cislo, phone,
            email, address, type_of_employment, monthly_income,
            amount, term
        )
        return loan_request