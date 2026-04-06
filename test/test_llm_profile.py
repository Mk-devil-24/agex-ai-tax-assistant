from agents.llm_profile_agent import extract_profile_with_gemini

print("Starting Gemini profile extraction...")

query = "I am salaried, pay rent, invested in PPF and ELSS, and want to reduce tax."
profile = extract_profile_with_gemini(query)

print("Result received:")
print(profile)
print("Done.")


