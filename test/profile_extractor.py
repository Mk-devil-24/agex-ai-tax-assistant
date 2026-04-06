def extract_persona(user_query: str) -> str:
    query = user_query.lower()

    salaried_keywords = ["salary", "salaried", "form 16", "hra", "rent", "employer"]
    business_keywords = ["business", "shop", "gst", "invoice", "sales", "expense", "client"]

    if any(word in query for word in business_keywords):
        return "small_business"

    if any(word in query for word in salaried_keywords):
        return "salaried"

    return "unknown"


if __name__ == "__main__":
    user_query = input("Enter user query: ")
    persona = extract_persona(user_query)
    print("Detected persona:", persona)


