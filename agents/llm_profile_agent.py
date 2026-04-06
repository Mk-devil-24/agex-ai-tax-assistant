import json
import warnings
from google import genai
from google.genai.types import HttpOptions

warnings.filterwarnings("ignore", message=".*is not a valid TrafficType.*")

client = genai.Client(
    vertexai=True,
    project="agex-hackathon",
    location="global",
    http_options=HttpOptions(api_version="v1"),
)


def extract_profile_with_gemini(user_query: str) -> dict:
    prompt = f"""
You are an information extraction agent for an Indian tax planning assistant.

Extract the user's tax-related profile from the text below.

Return ONLY valid JSON with these exact keys:
persona
rent_paid
has_gst_concern
has_investments
investment_mentions
expense_mentions

Rules:
- persona must be one of: "salaried", "small_business", "unknown"
- rent_paid must be true, false, or null
- has_gst_concern must be true, false, or null
- has_investments must be true, false, or null
- investment_mentions must be a JSON array of lowercase strings
- expense_mentions must be a JSON array of lowercase strings
- do not include any extra text
- do not wrap the JSON in markdown

User text:
{user_query}
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
    )

    text = response.text.strip()
    return json.loads(text)


