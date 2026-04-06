def generate_recommendations(profile: dict) -> list[str]:
    recommendations = []

    persona = profile["persona"]

    if persona == "salaried":
        recommendations.append("Compare old vs new tax regime before making fresh tax-saving investments.")

        if profile["rent_paid"]:
            recommendations.append("Check whether you can claim HRA benefit based on your rent payments.")

        if not profile["investment_mentions"]:
            recommendations.append("Review tax-saving options under 80C such as PPF, ELSS, NPS, insurance, or tax saver FD.")
        else:
            recommendations.append(
                f"You already mentioned these tax-saving items: {', '.join(profile['investment_mentions'])}. Check whether your 80C limit is fully utilized."
            )

    elif persona == "small_business":
        recommendations.append("Keep personal and business expenses separate for cleaner tax planning and compliance.")

        if profile["has_gst_concern"]:
            recommendations.append("Review GST applicability, registration status, and filing frequency carefully.")

        if profile["expense_mentions"]:
            recommendations.append(
                f"You mentioned these business expenses: {', '.join(profile['expense_mentions'])}. Check which of them are valid business deductions."
            )
        else:
            recommendations.append("Prepare a list of major business expenses like rent, internet, travel, electricity, laptop, or staff costs.")

    else:
        recommendations.append("First identify whether the user is salaried or a small business owner before generating tax advice.")

    return recommendations


if __name__ == "__main__":
    sample_profile = {
        "persona": "salaried",
        "rent_paid": True,
        "has_gst_concern": False,
        "investment_mentions": ["ppf", "elss"],
        "expense_mentions": []
    }

    recs = generate_recommendations(sample_profile)

    print("\nRecommendations:\n")
    for i, rec in enumerate(recs, start=1):
        print(f"{i}. {rec}")


