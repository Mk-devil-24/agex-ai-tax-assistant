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
        print("Workflow log insert failed:", errors)


