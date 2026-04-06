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
        "summary": f"persona={persona}, rent_paid={'rent' in query}, gst={'gst' in query}"
    }

    return profile


if __name__ == "__main__":
    user_query = input("Enter user query: ")
    profile = extract_profile_details(user_query)

    print("\nExtracted profile:\n")
    for key, value in profile.items():
        print(f"{key}: {value}")


