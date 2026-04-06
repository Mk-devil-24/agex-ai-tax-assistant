from agents.llm_document_agent import generate_documents_with_gemini


def generate_documents(profile: dict) -> list[str]:
    documents = []
    persona = profile["persona"]

    if persona == "salaried":
        documents.append("Form 16")
        if profile["rent_paid"] is True:
            documents.append("Rent receipts")
        if profile["has_investments"] is True:
            documents.append("Investment proofs")
        documents.append("Bank statements if needed")

    elif persona == "small_business":
        documents.append("Sales invoices")
        documents.append("Expense bills")
        documents.append("Bank statements")
        if profile["has_gst_concern"] is True:
            documents.append("GST registration and return records")

    return documents

def generate_documents_with_fallback(profile: dict) -> list[str]:
    try:
        llm_documents = generate_documents_with_gemini(profile)

        if isinstance(llm_documents, list) and all(isinstance(item, str) for item in llm_documents):
            return llm_documents

        print("Gemini document output invalid, using fallback.")
        return generate_documents(profile)

    except Exception as e:
        print("Gemini documents failed, using fallback:", e)
        return generate_documents(profile)



