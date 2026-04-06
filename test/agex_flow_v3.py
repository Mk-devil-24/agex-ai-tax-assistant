from google.cloud import bigquery


def extract_profile_details(user_query: str) -> dict:
    query = user_query.lower()

    salaried_keywords = ["salary", "salaried", "form 16", "hra", "rent", "employer"]
    business_keywords = ["business", "shop", "gst", "invoice", "sales", "expense", "client"]

    if any(word in query for word in business_keywords):
        persona = "small_business"
    elif any(word in query for word in salaried_keywords):
        persona = "salaried"
    else:
        persona = "unknown"

    investment_mentions = []
    for item in ["ppf", "elss", "nps", "insurance", "fd"]:
        if item in query:
            investment_mentions.append(item)

    expense_mentions = []
    for item in ["rent", "internet", "travel", "laptop", "staff", "electricity"]:
        if item in query:
            expense_mentions.append(item)

    profile = {
        "persona": persona,
        "rent_paid": "rent" in query,
        "has_gst_concern": "gst" in query,
        "investment_mentions": investment_mentions,
        "expense_mentions": expense_mentions,
    }

    return profile


def generate_followup_question(profile: dict) -> str | None:
    persona = profile["persona"]

    if persona == "unknown":
        return "Are you a salaried individual or a small business owner?"

    if persona == "salaried":
        rent_known = profile["rent_paid"]
        has_investments = len(profile["investment_mentions"]) > 0

        if not rent_known and not has_investments:
            return "Do you pay rent, and have you invested in tax-saving options like PPF, ELSS, NPS, insurance, or tax saver FD?"
        if not rent_known:
            return "Do you pay rent?"
        if not has_investments:
            return "Have you invested in tax-saving options like PPF, ELSS, NPS, insurance, or tax saver FD?"

    if persona == "small_business":
        gst_known = profile["has_gst_concern"]
        has_expenses = len(profile["expense_mentions"]) > 0

        if not gst_known and not has_expenses:
            return "Do you have GST-related concerns, and what major business expenses do you have, such as rent, internet, travel, laptop, electricity, or staff costs?"
        if not gst_known:
            return "Do you have any GST-related concerns or registration requirements?"
        if not has_expenses:
            return "What major business expenses do you have, such as rent, internet, travel, laptop, electricity, or staff costs?"

    return None


def fetch_tax_rules(persona: str):
    client = bigquery.Client()

    query = """
    SELECT title, category, description, applies_to
    FROM `agex-hackathon.agex_tax.tax_rules`
    WHERE applies_to IN (@persona, 'all')
    """

    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("persona", "STRING", persona)
        ]
    )

    return client.query(query, job_config=job_config).result()


def generate_recommendations(profile: dict) -> list[str]:
    recommendations = []
    persona = profile["persona"]

    if persona == "salaried":
        recommendations.append("Compare old vs new tax regime before making fresh tax-saving investments.")
        if profile["rent_paid"]:
            recommendations.append("Check whether you can claim HRA benefit based on your rent payments.")
        if not profile["investment_mentions"]:
            recommendations.append("Review tax-saving options under 80C such as PPF, ELSS, NPS, insurance, or tax saver FD.")
        else:
            recommendations.append(
                f"You already mentioned these tax-saving items: {', '.join(profile['investment_mentions'])}. Check whether your 80C limit is fully utilized."
            )

    elif persona == "small_business":
        recommendations.append("Keep personal and business expenses separate for cleaner tax planning and compliance.")
        if profile["has_gst_concern"]:
            recommendations.append("Review GST applicability, registration status, and filing frequency carefully.")
        if profile["expense_mentions"]:
            recommendations.append(
                f"You mentioned these business expenses: {', '.join(profile['expense_mentions'])}. Check which of them are valid business deductions."
            )
        else:
            recommendations.append("Prepare a list of major business expenses like rent, internet, travel, electricity, laptop, or staff costs.")

    return recommendations


def generate_tasks(profile: dict) -> list[str]:
    tasks = []
    persona = profile["persona"]

    if persona == "salaried":
        tasks.append("Compare old vs new tax regime.")
        if profile["rent_paid"]:
            tasks.append("Collect rent receipts for HRA review.")
        if profile["investment_mentions"]:
            tasks.append("Check whether your 80C limit is fully utilized.")
        else:
            tasks.append("Review 80C investment options like PPF, ELSS, NPS, insurance, or tax saver FD.")

    elif persona == "small_business":
        tasks.append("Separate personal and business expenses.")
        if profile["has_gst_concern"]:
            tasks.append("Review GST registration status and filing requirements.")
        if profile["expense_mentions"]:
            tasks.append("Organize proof for business expenses you mentioned.")
        else:
            tasks.append("Prepare a list of major business expenses.")

    return tasks


def generate_documents(profile: dict) -> list[str]:
    documents = []
    persona = profile["persona"]

    if persona == "salaried":
        documents.append("Form 16")
        if profile["rent_paid"]:
            documents.append("Rent receipts")
        documents.append("Investment proofs")
        documents.append("Bank statements if needed")

    elif persona == "small_business":
        documents.append("Sales invoices")
        documents.append("Expense bills")
        documents.append("Bank statements")
        if profile["has_gst_concern"]:
            documents.append("GST registration and return records")

    return documents


if __name__ == "__main__":
    user_query = input("Enter user query: ")

    profile = extract_profile_details(user_query)
    followup = generate_followup_question(profile)

    print("\nExtracted profile:")
    for key, value in profile.items():
        print(f"{key}: {value}")

    if followup:
        print("\nAGEX follow-up question:")
        print(followup)
    else:
        print("\nMatching tax rules:\n")
        rows = fetch_tax_rules(profile["persona"])
        for row in rows:
            print(f"Title: {row.title}")
            print(f"Category: {row.category}")
            print(f"Description: {row.description}")
            print(f"Applies To: {row.applies_to}")
            print("-" * 40)

        recommendations = generate_recommendations(profile)
        print("\nAGEX recommendations:\n")
        for i, rec in enumerate(recommendations, start=1):
            print(f"{i}. {rec}")

        tasks = generate_tasks(profile)
        print("\nAction tasks:\n")
        for i, task in enumerate(tasks, start=1):
            print(f"{i}. {task}")

        documents = generate_documents(profile)
        print("\nDocument checklist:\n")
        for i, doc in enumerate(documents, start=1):
            print(f"{i}. {doc}")


