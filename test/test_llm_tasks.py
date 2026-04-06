from agents.llm_task_agent import generate_tasks_with_gemini

profile = {
    "persona": "salaried",
    "rent_paid": True,
    "has_gst_concern": None,
    "has_investments": True,
    "investment_mentions": ["ppf", "elss"],
    "expense_mentions": []
}

result = generate_tasks_with_gemini(profile)

print("Gemini tasks:")
for i, item in enumerate(result, start=1):
    print(f"{i}. {item}")


