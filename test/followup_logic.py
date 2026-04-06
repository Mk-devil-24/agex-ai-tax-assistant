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


if __name__ == "__main__":
    user_query = input("Enter user query: ")
    profile = extract_profile_details(user_query)
    followup = generate_followup_question(profile)

    print("\nExtracted profile:")
    for key, value in profile.items():
        print(f"{key}: {value}")

    print("\nFollow-up question:")
    print(followup if followup else "No follow-up needed.")


