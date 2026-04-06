from google import genai
from google.genai.types import HttpOptions

client = genai.Client(
    vertexai=True,
    project="agex-hackathon",
    location="global",
    http_options=HttpOptions(api_version="v1"),
)

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="Reply with only this text: Vertex AI Gemini is working.",
)

print(response.text)


