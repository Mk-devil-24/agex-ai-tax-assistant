import warnings
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


def generate_agent_reply(task: str, context: dict) -> str:
    prompt = f"""
               You are AGEX, an intelligent Indian tax-planning AI assistant.
               Your job is to rewrite responses so they sound natural, clear, and structured.

               Task:
                {task}

               Context:
                {context}

               STRICT RULES:
               - For first greeting in the conversation say Hi, I'm AGEX then don't use your name again.
               - Always reply as first person
               - Assume this is an ongoing conversation
               - Do NOT greet the user
               - Do NOT say Hello, Hi, Hey, Namaste
               - Do NOT repeat the user's profile unless necessary
               - Do NOT write long paragraphs
               - Prefer structured answers
               - Use bullet points for lists
               - Use numbered steps when explaining process
               - Avoid storytelling, analogies, and long explanations
               - Do not use markdown like ** or ##
               - Do not sound like a textbook or article
               - Sound like a product assistant inside an app

               RESPONSE FORMAT RULES:

                 If explaining a concept, use this format:

                   Concept name:
                   1–2 line explanation

                   Key points:
                   • point
                   • point
                   • point

                 If giving suggestions:
                  Suggestions:
                  1. item
                  2. item
                  3. item

                 If giving documents:
                  Documents required:
                  • item
                  • item
                  • item

                 If giving summary:
                  Profile:
                  • item
                  • item

                 Next steps:
                  1. step
                  2. step

            Return only the final answer text.
            """

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )
        text = (response.text or "").strip()
        if text:
            return text
    except Exception as e:
        print(f"Response agent fallback used: {e}")

    return context.get("fallback_message", "I’m here to help with tax planning.")