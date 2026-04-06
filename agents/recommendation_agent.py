from agents.llm_recommendation_agent import generate_recommendations_with_gemini


def generate_recommendations(profile: dict) -> list[str]:
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


def generate_recommendations_with_fallback(profile: dict) -> list[str]:
    try:
        llm_recommendations = generate_recommendations_with_gemini(profile)

        if isinstance(llm_recommendations, list) and len(llm_recommendations) > 0:
            return llm_recommendations

        print("Gemini returned empty recommendations. Using fallback.")
        return generate_recommendations(profile)

    except Exception as e:
        print(f"LLM recommendation failed, using fallback: {e}")
        return generate_recommendations(profile)