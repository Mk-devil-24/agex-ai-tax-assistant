import requests

def get_document_checklist(persona, rent_paid, investments):
    response = requests.post(
        "http://localhost:9002/document-checklist",
        json={
            "persona": persona,
            "rent_paid": rent_paid,
            "investments": investments
        }
    )
    return response.json()