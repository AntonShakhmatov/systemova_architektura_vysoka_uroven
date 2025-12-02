# app/mailing/mailing.py
import json
from mailing.req import fetch_user_profiles
from mailing.server import sender


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
        loan_score: float,
        risk_level: str,
        reason: str,
    ) -> str:
        # reason у тебя JSON-строка: попробуем красиво распарсить
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
                subject=f"Scoring result: {user.get('name','')} {user.get('lastname','')}",
                body=body,
            )
