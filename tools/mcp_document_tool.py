from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class DocumentRequest(BaseModel):
    persona: str
    rent_paid: bool = False
    investments: bool = False

@app.post("/document-checklist")
def document_checklist(data: DocumentRequest):
    documents = ["PAN Card", "Aadhaar Card", "Bank Statements"]

    if data.rent_paid:
        documents.append("Rent Receipts")
        documents.append("Landlord PAN")

    if data.investments:
        documents.append("PPF Statement")
        documents.append("ELSS Statement")
        documents.append("Insurance Premium Receipts")

    if data.persona == "business":
        documents.append("GST Returns")
        documents.append("Profit & Loss Statement")

    return {
        "documents": documents,
        "message": "Document checklist generated"
    }