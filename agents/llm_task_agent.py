import warnings
import json
from google import genai
from google.genai.types import HttpOptions
from google.oauth2 import service_account

warnings.filterwarnings(
    "ignore",
    message=".*is not a valid TrafficType.*",
)

PROJECT_ID = "agex-hackathon"
LOCATION = "global"
CREDENTIALS_PATH = "/home/mkdevil24/agex/credentials/service-account.json"

credentials = service_account.Credentials.from_service_account_file(
    CREDENTIALS_PATH,
    scopes=["https://www.googleapis.com/auth/cloud-platform"],
)

client = genai.Client(
    vertexai=True,
    project=PROJECT_ID,
    location=LOCATION,
    credentials=credentials,
    http_options=HttpOptions(api_version="v1"),
)


def generate_tasks_with_gemini(profile: dict) -> list[str]:
    prompt = f"""
You are an Indian tax workflow task agent.

Based on the user profile below, return ONLY valid JSON.
The JSON must be an array of short action-task strings.

Rules:
- Maximum 6 tasks
- Keep them actionable
- Focus on tax planning and compliance preparation
- If persona is salaried, think about HRA, regime comparison, investment proof collection, and deduction review
- If persona is small_business, think about GST checks, expense proof organization, and compliance preparation
- No markdown
- No extra text

User profile:
{json.dumps(profile)}
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
    )

    text = response.text.strip()
    return json.loads(text)


