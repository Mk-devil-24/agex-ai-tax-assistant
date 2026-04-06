def classify_intent(user_query: str) -> str:
    query = user_query.lower().strip()

    greetings = [
        "hi", "hello", "hey", "good morning", "good evening", "good afternoon"
    ]

    goodbye_words = [
        "bye",
        "goodbye",
        "good bye",
        "see you",
        "see you later",
        "talk later",
        "catch you later",
        "bye bye",
        "ok bye",
        "okay bye",
        "thanks bye",
        "thank you bye",
        "that’s all",
        "thats all",
        "done",
        "we are done",
        "exit",
        "close chat",
    ]

    wellbeing = [
        "how are you", "how are you doing", "how are u"
    ]

    introductions = [
        "who are you", "what are you", "introduce yourself"
    ]

    capabilities = [
        "what can you do", "how can you help", "your scope",
        "your capabilities", "what do you help with"
    ]

    gratitude_words = [
        "thanks", "thank you", "thankyou", "thx", "thanks a lot", "many thanks"
    ]

    acknowledgement_words = [
        "okay", "ok", "got it", "alright", "fine", "noted", "cool"
    ]

    explanation_keywords = [
        "what is", "explain", "meaning", "define", "how does", "difference between"
    ]

    investment_keywords = [
        "suggest investments",
        "investment advice",
        "tax saving investments",
        "where should i invest",
        "what should i invest in",
        "investment options",
        "where to invest",
        "how should i invest",
        "advise investments",
        "where can i invest",
        "how can i save tax through investment",
        "how to invest to save tax",
        "best tax saving investment",
        "tax saver options",
    ]

    document_keywords = [
        "what documents",
        "documents required",
        "document checklist",
        "which documents",
        "tax documents",
        "what documents do i need",
        "documents needed",
        "what proof do i need",
        "what papers do i need",
    ]

    reminder_keywords = [
        "remind me",
        "set reminder",
        "create reminder",
        "tax deadline",
        "filing reminder",
        "set a reminder",
        "reminder for tax",
        "remind me to file tax",
        "remind me to file income tax",
        "set reminder to file tax",
    ]

    tax_keywords = [
        "tax", "gst", "salary", "salaried", "hra", "ppf", "elss", "nps",
        "business", "rent", "deduction", "compliance", "form 16",
        "income tax", "tax saving", "expenses", "invoice",
        "save tax", "reduce tax"
    ]

    # goodbye first for phrases like "thanks bye"
    if any(item in query for item in goodbye_words):
        return "goodbye"

    if any(item in query for item in wellbeing):
        return "wellbeing"

    if any(item in query for item in introductions):
        return "introduction"

    if any(item in query for item in capabilities):
        return "capabilities"

    # greeting should be exact-ish to avoid false matches
    if query in greetings or any(query.startswith(f"{greet} ") for greet in greetings):
        return "greeting"

    if any(item in query for item in gratitude_words):
        return "gratitude"

    if query in acknowledgement_words:
        return "acknowledgement"

    if any(item in query for item in explanation_keywords):
        return "explanation"

    if any(item in query for item in investment_keywords):
        return "investment_tool"

    if any(item in query for item in document_keywords):
        return "document_tool"

    if any(item in query for item in reminder_keywords):
        return "reminder_tool"

    if any(item in query for item in tax_keywords):
        return "tax_workflow"

    return "general"