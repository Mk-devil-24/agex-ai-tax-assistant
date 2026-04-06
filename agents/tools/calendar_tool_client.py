import requests

def create_tax_reminder(task, date):
    response = requests.post(
        "http://localhost:9003/create-reminder",
        json={
            "task": task,
            "date": date
        }
    )
    return response.json()