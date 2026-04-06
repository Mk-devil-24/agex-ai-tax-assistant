from google.cloud import bigquery

client = bigquery.Client()

persona = "small_business"  # change this to "small_business" to test

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

rows = client.query(query, job_config=job_config).result()

print(f"\nTax rules for persona: {persona}\n")

for row in rows:
    print(f"Title: {row.title}")
    print(f"Category: {row.category}")
    print(f"Description: {row.description}")
    print(f"Applies To: {row.applies_to}")
    print("-" * 40)


