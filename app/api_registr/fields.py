from pydantic import BaseModel

class LoanHistoryActive(BaseModel):
    opened_date: str
    remaining_balance: float
    monthly_installment: float
    status: str  # e.g., "active", "closed", "defaulted"\

class LoanHistoryClosed(BaseModel):
    opened_date: str
    closed_date: str
    total_paid: float
    status: str  # e.g., "closed", "defaulted"

class DelinquencyDates(BaseModel):
    current_arrears_days: int
    max_arrears_12_months: int
    max_arrears_lifetime: int
    arrearc_dates_12_months: list[str]  # List of dates in "YYYY-MM-DD" format
    has_written_off_loans: bool
    has_restructurings: bool

class FinancialObligations(BaseModel):
    monthly_obligations: float
    total_outstanding_loans: float
    number_of_active_loans: int
    number_of_closed_loans: int

class Enquiries(BaseModel):
    enquiries_last_6_months: int
    enquiries_last_12_months: int
    enquiries_rejected_applications: int
    recent_inquiries_details: list[str]  # List of inquiry details

class RiskFlags(BaseModel):
    risk_score: float
    risk_bands: str  # e.g., "low", "medium", "high"
    fraud_flags: list[str]  # List of fraud flag descriptions
    adress_missmatch: bool
    identity_consistency_score: float
   