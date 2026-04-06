import requests

KNOWLEDGE_TOOL_URL = "http://localhost:9004/knowledge-search"

def search_knowledge(query):
    try:
        print("\n[KNOWLEDGE CLIENT] Sending query:", query)
        print("[KNOWLEDGE CLIENT] URL:", KNOWLEDGE_TOOL_URL)

        response = requests.post(
            KNOWLEDGE_TOOL_URL,
            json={"query": query},
            timeout=10
        )

        print("[KNOWLEDGE CLIENT] Status code:", response.status_code)
        print("[KNOWLEDGE CLIENT] Raw response text:", response.text)

        if response.status_code != 200:
            return {
                "status": "error",
                "message": f"Knowledge API returned {response.status_code}: {response.text}"
            }

        try:
            data = response.json()
        except Exception as json_error:
            print("[KNOWLEDGE CLIENT] JSON parse error:", str(json_error))
            return {
                "status": "error",
                "message": f"Knowledge API returned non-JSON response: {response.text}"
            }

        print("[KNOWLEDGE CLIENT] Parsed JSON:", data)

        final_data = {
            "status": "success",
            "concept": data.get("concept"),
            "explanation": data.get("explanation"),
            "key_points": data.get("key_points", [])
        }

        print("[KNOWLEDGE CLIENT] Final structured data:", final_data)
        return final_data

    except Exception as e:
        print("[KNOWLEDGE CLIENT] ERROR:", str(e))
        return {
            "status": "error",
            "message": str(e)
        }