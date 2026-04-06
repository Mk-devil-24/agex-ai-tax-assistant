from fastapi import FastAPI
from pydantic import BaseModel
from google import genai
import json
import re
import traceback

app = FastAPI()

print("KNOWLEDGE API LOADED - DEBUG VERSION")

client = genai.Client(
    vertexai=True,
    project="agex-hackathon",
    location="us-central1"
)

class KnowledgeRequest(BaseModel):
    query: str

def fallback_parse_text(query: str, text: str):
    text = (text or "").strip()

    concept = query
    explanation = text
    key_points = []

    if "Key points:" in text:
        parts = text.split("Key points:", 1)
        before_points = parts[0].strip()
        after_points = parts[1].strip()

        if ":" in before_points:
            concept_part, explanation_part = before_points.split(":", 1)
            concept = concept_part.strip()
            explanation = explanation_part.strip()
        else:
            explanation = before_points

        for line in after_points.splitlines():
            line = line.strip()
            if not line:
                continue
            line = line.lstrip("•*- ").strip()
            if line:
                key_points.append(line)
    else:
        if ":" in text:
            concept_part, explanation_part = text.split(":", 1)
            concept = concept_part.strip()
            explanation = explanation_part.strip()

    return {
        "concept": concept,
        "explanation": explanation,
        "key_points": key_points
    }

@app.post("/knowledge-search")
def knowledge_search(request: KnowledgeRequest):
    try:
        print("\n[KNOWLEDGE API] Incoming query:", request.query)

        prompt = f"""
You are an Indian tax assistant.

Convert the following tax concept into structured JSON.

Query: {request.query}

STRICT RULES:
- Return only JSON
- Do not greet
- Do not say Hello, Hi, Hey, Namaste
- Do not use markdown
- Do not use bold text
- Keep explanation short
- key_points must be short strings
- Do not write anything outside JSON

Return in exactly this format:
{{
  "concept": "",
  "explanation": "",
  "key_points": ["", "", "", ""]
}}
"""

        print("[KNOWLEDGE API] Prompt sent to model:")
        print(prompt)

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        text = (response.text or "").strip()

        print("[KNOWLEDGE API] Raw model response:")
        print(text)

        try:
            match = re.search(r"\{.*\}", text, re.DOTALL)

            if match:
                json_text = match.group()
                print("[KNOWLEDGE API] Extracted JSON:")
                print(json_text)

                parsed = json.loads(json_text)
                print("[KNOWLEDGE API] Parsed JSON object:")
                print(parsed)
                return parsed

        except Exception as parse_error:
            print("[KNOWLEDGE API] JSON parse failed:", str(parse_error))

        fallback = fallback_parse_text(request.query, text)
        print("[KNOWLEDGE API] Fallback structured object:")
        print(fallback)
        return fallback

    except Exception as e:
        print("[KNOWLEDGE API] SERVER ERROR:", str(e))
        traceback.print_exc()
        return {
            "concept": request.query,
            "explanation": f"Knowledge API server error: {str(e)}",
            "key_points": []
        }