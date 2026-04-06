from google.cloud import bigquery


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

    rows = client.query(query, job_config=job_config).result()

    return [
        {
            "title": row.title,
            "category": row.category,
            "description": row.description,
            "applies_to": row.applies_to,
        }
        for row in rows
    ]


