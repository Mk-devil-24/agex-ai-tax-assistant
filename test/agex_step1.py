from google.cloud import bigquery


def extract_persona(user_query: str) -> str:
    query = user_query.lower()

    salaried_keywords = ["salary", "salaried", "form 16", "hra", "rent", "employer"]
    business_keywords = ["business", "shop", "gst", "invoice", "sales", "expense", "client"]

    if any(word in query for word in business_keywords):
        return "small_business"

    if any(word in query for word in salaried_keywords):
        return "salaried"

    return "unknown"


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


if __name__ == "__main__":
    user_query = input("Enter user query: ")

    persona = extract_persona(user_query)
    print("\nDetected persona:", persona)

    if persona == "unknown":
        print("Could not detect persona clearly.")
    else:
        rows = fetch_tax_rules(persona)

        print("\nMatching tax rules:\n")
        for row in rows:
            print(f"Title: {row.title}")
            print(f"Category: {row.category}")
            print(f"Description: {row.description}")
            print(f"Applies To: {row.applies_to}")
            print("-" * 40)


