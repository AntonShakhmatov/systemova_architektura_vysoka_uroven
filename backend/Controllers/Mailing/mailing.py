# app/Controllers/Mailing/mailing.py
import json
from Controllers.Mailing.req import fetch_user_profiles
from Services.Mailing.server import sender


class Mailing:
    def __init__(self, port, smtp_server, sender_email, receiver_email, password):
        self.port = port
        self.smtp_server = smtp_server
        self.sender_email = sender_email
        self.receiver_email = receiver_email
        self.password = password

    @staticmethod
    def collect_for_mail(
        name: str,
        lastname: str,
        birthdate: str,
        rodne_cislo: str,
        employment_place: str,
        employment_type: str,
        monthly_income:float,
        loan_amount: float,
        term: int,
        total_monthly_installment: float,
        loan_score: float,
        risk_level: str,
        reason: str,
    ) -> str:
        
        reason_pretty = reason
        try:
            parsed = json.loads(reason) if reason else []
            if isinstance(parsed, list):
                reason_pretty = "\n".join(f"- {x}" for x in parsed) or "—"
        except Exception:
            pass

        return (
            f"Loan application result\n"
            f"----------------------\n"
            f"Name: {name}\n"
            f"Lastname: {lastname}\n"
            f"Birthdate: {birthdate}\n"
            f"Rodne cislo: {rodne_cislo}\n"
            f"Employment place: {employment_place}\n"
            f"Employment type: {employment_type}\n"
            f"Monthly income: {monthly_income}\n"
            f"Loan amount: {loan_amount}\n"
            f"Term: {term}\n"
            f"Total monthly installment: {total_monthly_installment}\n"
            f"\n"
            f"Loan score: {loan_score}\n"
            f"Risk level: {risk_level}\n"
            f"Reason:\n{reason_pretty}\n"
        )

    def process_all_users(self) -> None:
        profiles = fetch_user_profiles()

        for user in profiles:
            body = self.collect_for_mail(
                name=user.get("name", ""),
                lastname=user.get("lastname", ""),
                birthdate=str(user.get("birthdate", "")),
                rodne_cislo=user.get("rodne_cislo", ""),
                employment_place=user.get("employment_place", ""),
                employment_type=user.get("employment_type", ""),
                monthly_income=user.get("monthly_income", ""),
                loan_amount=user.get("loan_amount",""),
                term=user.get("term", ""),
                total_monthly_installment=user.get("total_monthly_installment", ""),
                loan_score=user.get("loan_score", ""),
                risk_level=user.get("risk_level", ""),
                reason=user.get("reason", ""),
            )

            sender(
                port=self.port,
                smtp_server=self.smtp_server,
                sender_email=self.sender_email,
                receiver_email=self.receiver_email,
                password=self.password,
                subject=f"Scoring result: {user.get('user_id', '')} {user.get('name','')} {user.get('lastname','')}",
                body=body,
            )
