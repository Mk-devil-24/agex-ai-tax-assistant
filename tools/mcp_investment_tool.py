from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class InvestmentRequest(BaseModel):
    persona: str
    income: float
    risk_level: str = "medium"

@app.post("/investment-suggestions")
def investment_suggestions(data: InvestmentRequest):
    suggestions = []

    if data.persona == "salaried":
        suggestions = [
            "ELSS Mutual Funds",
            "PPF (Public Provident Fund)",
            "EPF Contribution",
            "NPS (National Pension Scheme)",
            "Tax Saving Fixed Deposit"
        ]
    elif data.persona == "business":
        suggestions = [
            "NPS",
            "PPF",
            "Health Insurance (80D)",
            "Business Expense Deductions",
            "Depreciation Benefits"
        ]

    return {
        "suggestions": suggestions,
        "risk_level": data.risk_level,
        "message": "Investment suggestions generated"
    }