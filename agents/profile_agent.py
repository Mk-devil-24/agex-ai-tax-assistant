from agents.llm_profile_agent import extract_profile_with_gemini


def empty_profile():
    return {
        "persona": None,
        "rent_paid": None,
        "has_gst_concern": None,
        "has_investments": None,
    }


def normalize_profile(profile: dict):
    base = empty_profile()

    if not profile:
        return base

    for key in base.keys():
        value = profile.get(key)

        if key == "persona":
            if value in ["salaried", "business"]:
                base[key] = value
            elif value == "small_business":
                base[key] = "business"
            else:
                base[key] = None
        else:
            if value is True:
                base[key] = True
            elif value is False:
                base[key] = False
            else:
                base[key] = None

    return base


def extract_profile_details_with_fallback(text: str) -> dict:
    text = text.lower()

    profile = {}

    # Persona
    if "salaried" in text or "salary" in text:
        profile["persona"] = "salaried"

    elif "business" in text or "gst" in text:
        profile["persona"] = "business"

    # Rent
    if "rent" in text:
        if "no" in text or "not" in text:
            profile["rent_paid"] = False
        else:
            profile["rent_paid"] = True

    # Investments
    if "investment" in text:
        if "no" in text:
            profile["has_investments"] = False
        else:
            profile["has_investments"] = True

    # GST
    if "gst" in text:
        if "no" in text:
            profile["has_gst_concern"] = False
        else:
            profile["has_gst_concern"] = True

    return profile

# -------------------------
# SAFE MERGE (CRITICAL FIX)
# -------------------------
def merge_profiles(old_profile, new_profile):
    merged = old_profile.copy()

    for key, value in new_profile.items():
        if value is not None:
            # 🚨 DO NOT overwrite existing persona
            if key == "persona" and merged.get("persona") is not None:
                continue
            merged[key] = value

    return merged


# -------------------------
# FOLLOW-UP QUESTIONS
# -------------------------
def generate_followup_question(profile: dict) -> str | None:
    persona = profile.get("persona")
    rent_paid = profile.get("rent_paid")
    has_investments = profile.get("has_investments")
    has_gst = profile.get("has_gst_concern")

    # Step 1
    if not persona:
        return "Are you salaried or running a business?"

    # Step 2 — Salaried
    if persona == "salaried":
        if rent_paid is None:
            return "Do you pay rent?"
        if has_investments is None:
            return "Have you invested in tax-saving options like PPF, ELSS, NPS, insurance, or tax saver FD?"
        return None

    # Step 3 — Business
    if persona == "business":
        if has_gst is None:
            return "Do you have GST registration?"
        if has_investments is None:
            return "Have you made any tax-saving investments?"
        return None

    return None