import json
from datetime import datetime, timezone
from google.cloud import bigquery


def save_workflow_log(
    user_query: str,
    profile: dict,
    recommendations: list[str],
    tasks: list[str],
    documents: list[str],
):
    client = bigquery.Client()

    table_id = "agex-hackathon.agex_tax.workflow_logs"

    rows_to_insert = [
        {
            "run_time": datetime.now(timezone.utc).isoformat(),
            "user_query": user_query,
            "persona": profile["persona"],
            "profile_json": json.dumps(profile),
            "recommendations_json": json.dumps(recommendations),
            "tasks_json": json.dumps(tasks),
            "documents_json": json.dumps(documents),
        }
    ]

    errors = client.insert_rows_json(table_id, rows_to_insert)

    if errors:
        print("Insert failed:")
        print(errors)
    else:
        print("Workflow log saved successfully.")


if __name__ == "__main__":
    sample_profile = {
        "persona": "salaried",
        "rent_paid": True,
        "has_gst_concern": None,
        "has_investments": True,
        "investment_mentions": ["ppf", "elss"],
        "expense_mentions": []
    }

    sample_recommendations = [
        "Compare old vs new tax regime.",
        "Check HRA benefit."
    ]

    sample_tasks = [
        "Collect rent receipts",
        "Review 80C utilization"
    ]

    sample_documents = [
        "Form 16",
        "Rent receipts",
        "Investment proofs"
    ]

    save_workflow_log(
        user_query="I am salaried, pay rent, and invested in PPF and ELSS",
        profile=sample_profile,
        recommendations=sample_recommendations,
        tasks=sample_tasks,
        documents=sample_documents,
    )


