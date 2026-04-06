import requests

def get_investment_suggestions(persona, income):
    response = requests.post(
        "http://localhost:9001/investment-suggestions",
        json={
            "persona": persona,
            "income": income
        }
    )
    return response.json()