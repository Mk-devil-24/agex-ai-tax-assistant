def generate_tasks(profile: dict) -> list[str]:
    tasks = []

    persona = profile["persona"]

    if persona == "salaried":
        tasks.append("Compare old vs new tax regime.")
        if profile["rent_paid"]:
            tasks.append("Collect rent receipts for HRA review.")
        if profile["investment_mentions"]:
            tasks.append("Check whether your 80C limit is fully utilized.")
        else:
            tasks.append("Review 80C investment options like PPF, ELSS, NPS, insurance, or tax saver FD.")

    elif persona == "small_business":
        tasks.append("Separate personal and business expenses.")
        if profile["has_gst_concern"]:
            tasks.append("Review GST registration status and filing requirements.")
        if profile["expense_mentions"]:
            tasks.append("Organize proof for business expenses you mentioned.")
        else:
            tasks.append("Prepare a list of major business expenses.")

    return tasks


def generate_documents(profile: dict) -> list[str]:
    documents = []

    persona = profile["persona"]

    if persona == "salaried":
        documents.append("Form 16")
        if profile["rent_paid"]:
            documents.append("Rent receipts")
        documents.append("Investment proofs")
        documents.append("Bank statements if needed")

    elif persona == "small_business":
        documents.append("Sales invoices")
        documents.append("Expense bills")
        documents.append("Bank statements")
        if profile["has_gst_concern"]:
            documents.append("GST registration and return records")

    return documents


if __name__ == "__main__":
    sample_profile = {
        "persona": "salaried",
        "rent_paid": True,
        "has_gst_concern": False,
        "investment_mentions": ["ppf", "elss"],
        "expense_mentions": []
    }

    tasks = generate_tasks(sample_profile)
    documents = generate_documents(sample_profile)

    print("\nTasks:")
    for i, task in enumerate(tasks, start=1):
        print(f"{i}. {task}")

    print("\nDocuments:")
    for i, doc in enumerate(documents, start=1):
        print(f"{i}. {doc}")


