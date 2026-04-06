from agents.llm_document_agent import generate_documents_with_gemini

profile = {
    "persona": "small_business",
    "rent_paid": None,
    "has_gst_concern": True,
    "has_investments": None,
    "investment_mentions": [],
    "expense_mentions": ["internet", "travel", "staff"]
}

result = generate_documents_with_gemini(profile)

print("Gemini documents:")
for i, item in enumerate(result, start=1):
    print(f"{i}. {item}")


