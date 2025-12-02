# app/api_register/loan_history.py
import requests
import csv
import os
from urllib.parse import quote
from api_registr.req import fetch_user_profiles

def normalize_birthdate(birthdate: str) -> str:
    if not birthdate:
        return ""
    return str(birthdate).split(" ")[0].split("T")[0]

class LoanHistory:
    def __init__(self, save_path: str = "/app/uploads"):
        self.save_path = save_path
        os.makedirs(self.save_path, exist_ok=True)

    def fetch_loan_history(self, name: str, lastname: str, birthdate: str, rodne_cislo: str) -> dict:
        birthdate = normalize_birthdate(birthdate)

        url = (
            "https://registry.example.com/api/credit-check/"
            f"{quote(name)}/{quote(lastname)}/{quote(birthdate)}/{quote(rodne_cislo)}"
        )
        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"[warn] Could not fetch loan history for {name} {lastname}: {e}")
            return {"error": "Could not fetch loan history"}

    def save_loan_to_csv(self, history: dict, name: str, lastname: str, birthdate: str) -> None:
        # If API will return the error
        if "error" in history:
            print(f"Error in loan history for {name} {lastname}: {history['error']}")
            return

        loans = history.get("loans", [])
        if not loans:
            print(f"No loan history available for {name} {lastname}.")
            return

        filename = f"{name}_{lastname}_{birthdate}_loan_history.csv"
        filepath = os.path.join(self.save_path, filename)

        # fieldnames = list(loans[0].keys())
        fieldnames = [
            "opened_date",
            "closed_date",
            "remaining_balance",
            "monthly_installment",
            "credit_limit",
            "status",
            "current_arrears_days",
            "max_arrears_last_12m",
        ]

        rows = []
        for loan in loans:
            rows.append({
                "opened_date": loan.get("opened_date", ""),
                "closed_date": loan.get("closed_date", ""),
                "remaining_balance": loan.get("remaining_balance", 0),
                "monthly_installment": loan.get("monthly_installment", 0),
                "credit_limit": loan.get("credit_limit", ""),
                "status": str(loan.get("status", "")).lower(),
                "current_arrears_days": loan.get("current_arrears_days", 0),
                "max_arrears_last_12m": loan.get("max_arrears_last_12m", 0),
            })

        with open(filepath, mode="w", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(loans)

        print(f"Loan history saved to {filepath}")

    def process_all_users(self) -> None:

        profiles = fetch_user_profiles()

        for user in profiles:
            history = self.fetch_loan_history(
                name=user["name"],
                lastname=user["lastname"],
                birthdate=user["birthdate"],
                rodne_cislo=user["rodne_cislo"],
            )
            self.save_loan_to_csv(
                history,
                user["name"],
                user["lastname"],
                user["birthdate"],
            )



if __name__ == "__main__":
    lh = LoanHistory(save_path="/app/uploads")
    lh.process_all_users()