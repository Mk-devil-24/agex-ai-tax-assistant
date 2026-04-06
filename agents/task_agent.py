from agents.llm_task_agent import generate_tasks_with_gemini


def generate_tasks(profile: dict) -> list[str]:
    tasks = []
    persona = profile["persona"]

    if persona == "salaried":
        tasks.append("Compare old vs new tax regime.")
        if profile["rent_paid"] is True:
            tasks.append("Collect rent receipts for HRA review.")
        if profile["has_investments"] is True:
            tasks.append("Check whether your 80C limit is fully utilized.")
        elif profile["has_investments"] is False:
            tasks.append("Review 80C investment options like PPF, ELSS, NPS, insurance, or tax saver FD.")

    elif persona == "small_business":
        tasks.append("Separate personal and business expenses.")
        if profile["has_gst_concern"] is True:
            tasks.append("Review GST registration status and filing requirements.")
        if profile["expense_mentions"]:
            tasks.append("Organize proof for business expenses you mentioned.")
        else:
            tasks.append("Prepare a list of major business expenses.")

    return tasks

def generate_tasks_with_fallback(profile: dict) -> list[str]:
    try:
        llm_tasks = generate_tasks_with_gemini(profile)

        if isinstance(llm_tasks, list) and all(isinstance(item, str) for item in llm_tasks):
            return llm_tasks

        print("Gemini task output invalid, using fallback.")
        return generate_tasks(profile)

    except Exception as e:
        print("Gemini tasks failed, using fallback:", e)
        return generate_tasks(profile)



