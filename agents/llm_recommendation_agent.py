import warnings
import json
from typing import List
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


def _fallback_recommendations(profile: dict) -> List[str]:
    recommendations = []

    persona = profile.get("persona")
    rent_paid = profile.get("rent_paid")
    has_gst_concern = profile.get("has_gst_concern")
    has_investments = profile.get("has_investments")

    if persona == "salaried":
        if rent_paid is True:
            recommendations.append("Check whether you can claim HRA exemption for rent paid.")
        if has_investments is False:
            recommendations.append(
                "Consider tax-saving options under Section 80C such as PPF, ELSS, NPS, or tax saver FD."
            )
        recommendations.append("Compare old and new tax regime before filing.")
        recommendations.append("Review whether health insurance deduction under Section 80D applies to you.")

    elif persona in ["small_business", "business"]:
        if has_gst_concern is True:
            recommendations.append("Keep GST returns and invoices updated for compliance.")
        recommendations.append("Track eligible business expenses carefully for deductions.")
        recommendations.append("Separate personal and business expenses clearly.")
        recommendations.append("Maintain proper documentation for invoices, expenses, and tax filing.")

    else:
        recommendations.append("Review the applicable tax regime and available deductions.")
        recommendations.append("Check whether Section 80C and 80D benefits apply to you.")

    return recommendations[:5]


def generate_recommendations_with_gemini(profile: dict) -> List[str]:
    prompt = f"""
You are an Indian tax-planning recommendation agent.

Based on the user profile below, return ONLY valid JSON.
The JSON must be an array of short recommendation strings.

Rules:
- Maximum 5 recommendations
- Keep them practical
- Focus on tax planning and compliance
- If persona is salaried, think about rent, HRA, old vs new regime, and tax-saving investments
- If persona is small_business or business, think about GST, business expenses, documentation, and separation of personal/business expenses
- No markdown
- No extra text
- Output must be a valid JSON array of strings only

User profile:
{json.dumps(profile)}
"""

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )

        text = (response.text or "").strip()

        if not text:
            print("Gemini recommendations returned empty text. Using fallback.")
            return _fallback_recommendations(profile)

        try:
            parsed = json.loads(text)

            if isinstance(parsed, list):
                clean_items = [
                    str(item).strip()
                    for item in parsed
                    if isinstance(item, str) and str(item).strip()
                ]
                if clean_items:
                    return clean_items[:5]

            print("Gemini recommendations returned non-list JSON. Using fallback.")
            return _fallback_recommendations(profile)

        except json.JSONDecodeError:
            print("Gemini recommendations returned non-JSON output. Using fallback.")
            return _fallback_recommendations(profile)

    except Exception as e:
        print(f"Gemini recommendation call failed: {e}. Using fallback.")
        return _fallback_recommendations(profile)