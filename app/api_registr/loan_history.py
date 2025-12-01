import requests
import csv
import os


class LoanHistory:
    def __init__(self, save_path="../uploads/"):
        self.save_path = save_path
        os.makedirs(save_path, exist_ok=True)

    def fetch_loan_history(self, name: str, lastname: str, birthdate: str) -> dict:
        self.name = name
        self.lastname = lastname
        self.birthdate = birthdate

        url = f"https://registry.example.com/api/credit-check/{name}/{lastname}/{birthdate}"
        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            return response.json()
        except requests.RequestException:
            return {"error": "Could not fetch loan history"}

    def save_loan_to_csv(self, history: dict) -> None:
        loans = history.get("loans", [])

        if not loans:
            print("No loan history available to save.")
            return

        filename = f"{self.name}_{self.lastname}_{self.birthdate}_loan_history.csv"
        filepath = os.path.join(self.save_path, filename)

        fieldnames = list(loans[0].keys())

        with open(filepath, mode='w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for loan in loans:
                writer.writerow(loan)

        print(f"Loan history saved to {filepath}")

# vyvolanie
lh = LoanHistory()

history = lh.fetch_loan_history("John", "Doe", "1990-01-01")

lh.save_loan_to_csv(history)