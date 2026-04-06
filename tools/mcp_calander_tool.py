from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime

app = FastAPI()

class ReminderRequest(BaseModel):
    task: str
    date: str

@app.post("/create-reminder")
def create_reminder(data: ReminderRequest):
    return {
        "task": data.task,
        "date": data.date,
        "status": "Reminder scheduled",
        "created_at": str(datetime.now())
    }