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


def generate_documents_with_gemini(profile: dict) -> list[str]:
    prompt = f"""
You are an Indian tax document checklist agent.

Based on the user profile below, return ONLY valid JSON.
The JSON must be an array of short document/checklist item strings.

Rules:
- Maximum 6 items
- Keep them practical
- Focus on tax planning and compliance documents
- If persona is salaried, think about Form 16, rent receipts, investment proofs, and bank statements
- If persona is small_business, think about sales invoices, expense bills, GST records, and bank statements
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


