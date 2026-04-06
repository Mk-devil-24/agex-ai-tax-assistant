from agents.response_agent import generate_agent_reply


def handle_general_conversation(intent: str) -> dict:
    responses = {
        "greeting": (
            "Hi, I’m AGEX. I can help you with tax planning, tax-saving investments, "
            "and reminders for important tax dates. Let me know what you’d like help with."
        ),
        "wellbeing": (
            "I’m doing well, thank you. I’m here and ready to help you with tax planning "
            "or any related questions you have."
        ),
        "introduction": (
            "I’m AGEX, an AI tax planning assistant. I’m here to help you understand tax-related "
            "topics, explore deductions, check documents, and plan the next steps clearly."
        ),
        "capabilities": (
            "I can help you with tax planning, explain tax terms in simple language, suggest "
            "tax-saving investment options, prepare document checklists, and set reminders for key tax tasks."
        ),
        "gratitude": (
            "You’re welcome. I’m glad that helped, and I’m here if you want to continue with anything else."
        ),
        "acknowledgement": (
            "Got it. That helps, and we can continue from here whenever you're ready."
        ),
        "off_topic": (
            "I’m mainly here to help with tax planning and related topics, but if your question connects "
            "to tax, salary, investments, documents, or reminders, I can definitely help."
        ),
        "goodbye": (
            "Alright, If you need help again, I'll be right here. Bye!"
            "Bye! "
        ),
        "general": (
            "I’m here to help with tax planning and related questions. You can ask me about deductions, "
            "investments, documents, reminders, or tax terms anytime."
        ),
    }

    base_message = responses.get(intent, responses["general"])

    message = generate_agent_reply(
        task=(
            "Rewrite this assistant message so it sounds natural, slightly fuller, and human. "
            "Keep it as a paragraph. Do not use bullet points. Do not make it too short."
        ),
        context={
            "response_type": "general",
            "intent": intent,
            "conversation_stage": "ongoing",
            "base_message": base_message,
            "fallback_message": base_message,
        },
    )

    return {
        "status": "general",
        "message": message,
    }


def make_followup_conversational(profile: dict, question: str) -> str:
    q = (question or "").strip()
    q_lower = q.lower()

    if "salaried" in q_lower or "self-employed" in q_lower or "business" in q_lower:
        base_message = (
            "I can help with that. To guide you properly, I first need to understand your income type a little better. "
            f"{q}"
        )
    elif "rent" in q_lower:
        base_message = (
            "Rent can make a difference in the deductions available to you, so I just want to confirm one thing. "
            f"{q}"
        )
    elif "invest" in q_lower or "ppf" in q_lower or "elss" in q_lower or "nps" in q_lower:
        base_message = (
            "Tax-saving investments can reduce your taxable income quite a bit, so I want to check this as well. "
            f"{q}"
        )
    elif "gst" in q_lower:
        base_message = (
            "That detail will help me understand your tax situation more accurately. "
            f"{q}"
        )
    else:
        base_message = (
            "I need one quick detail before I continue, just so I can guide you properly. "
            f"{q}"
        )

    return generate_agent_reply(
        task=(
            "Rewrite this follow-up question so it sounds like a real assistant in an ongoing conversation. "
            "Keep it warm, natural, and a little fuller than a form question. "
            "Keep it as a paragraph and ask only one actual question."
        ),
        context={
            "response_type": "followup",
            "profile": profile,
            "question": question,
            "conversation_stage": "ongoing",
            "base_message": base_message,
            "fallback_message": base_message,
        },
    )


def make_completion_summary(profile: dict) -> str:
    persona = profile.get("persona")
    rent_paid = profile.get("rent_paid")
    has_investments = profile.get("has_investments")
    has_gst_concern = profile.get("has_gst_concern")

    if persona == "salaried":
        if rent_paid is True and has_investments is False:
            base_message = (
                "I’ve now prepared your tax planning guidance based on what you shared. "
                "From your profile, I understand that you are salaried, you do pay rent, "
                "and you have not yet invested in tax-saving options. "
                "From here, I can help you explore suitable investment options, check which documents you should keep ready, "
                "set reminders, or explain any tax term you want to understand better."
            )
        elif rent_paid is True and has_investments is True:
            base_message = (
                "I’ve now prepared your tax planning guidance based on what you shared. "
                "From your profile, I understand that you are salaried, you pay rent, "
                "and you already have some tax-saving investments in place. "
                "I can now help you review your investment options, check your documents, set reminders, "
                "or explain anything you want to understand more clearly."
            )
        elif rent_paid is False and has_investments is False:
            base_message = (
                "I’ve now prepared your tax planning guidance based on what you shared. "
                "From your profile, I understand that you are salaried, you do not pay rent, "
                "and you have not yet invested in tax-saving options. "
                "I can help you look at tax-saving investments, review documents, set reminders, "
                "or explain any tax concept step by step."
            )
        elif rent_paid is False and has_investments is True:
            base_message = (
                "I’ve now prepared your tax planning guidance based on what you shared. "
                "From your profile, I understand that you are salaried, you do not pay rent, "
                "and you already have tax-saving investments. "
                "If you want, I can help you review those options further, check your documents, set reminders, "
                "or explain related tax terms in simple language."
            )
        else:
            base_message = (
                "I’ve now prepared your tax planning guidance based on the information you provided. "
                "From here, I can also help you with investments, documents, reminders, "
                "or any tax-related explanation you need."
            )

    elif persona in ["business", "small_business"]:
        if has_gst_concern is True:
            base_message = (
                "I’ve now prepared your tax planning guidance based on what you shared. "
                "From your profile, I understand that you run a business and you do have GST-related concerns. "
                "From here, I can help you with document requirements, reminders, and explanations around tax and GST topics."
            )
        elif has_gst_concern is False:
            base_message = (
                "I’ve now prepared your tax planning guidance based on what you shared. "
                "From your profile, I understand that you run a business and you do not currently have GST-related concerns. "
                "I can still help you with documents, reminders, or any tax explanation you want to go through."
            )
        else:
            base_message = (
                "I’ve now prepared your tax planning guidance based on the information you provided. "
                "From here, I can also help you with documents, reminders, and tax explanations."
            )
    else:
        base_message = (
            "I’ve prepared your tax planning guidance based on the information you shared. "
            "If you want to continue, I can also help with investment suggestions, documents, reminders, "
            "or simple explanations of tax terms."
        )

    return generate_agent_reply(
        task=(
            "Rewrite this completion message so it feels warm, natural, and conversational. "
            "Keep it as a paragraph. Do not use bullet points. "
            "It should feel like a real assistant continuing the conversation."
        ),
        context={
            "response_type": "summary",
            "profile": profile,
            "conversation_stage": "ongoing",
            "base_message": base_message,
            "fallback_message": base_message,
        },
    )


def _extract_text_from_tool_data(tool_data, fallback: str) -> str:
    if tool_data is None:
        return fallback

    if isinstance(tool_data, str):
        cleaned = tool_data.strip()
        return cleaned if cleaned else fallback

    if isinstance(tool_data, list):
        if not tool_data:
            return fallback
        return "\n".join(f"- {item}" for item in tool_data)

    if isinstance(tool_data, dict):
        for key in [
            "answer",
            "message",
            "result",
            "content",
            "text",
            "response",
            "details",
            "summary",
            "description",
        ]:
            value = tool_data.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()

        suggestions = tool_data.get("suggestions") or tool_data.get("investments") or tool_data.get("options")
        if isinstance(suggestions, list) and suggestions:
            return "\n".join(f"- {item}" for item in suggestions)

        checklist = tool_data.get("checklist") or tool_data.get("documents") or tool_data.get("items")
        if isinstance(checklist, list) and checklist:
            return "\n".join(f"- {item}" for item in checklist)

        return fallback

    return str(tool_data)


def make_tool_response_conversational(tool_name: str, tool_data: dict, profile=None) -> str:
    tool_name = (tool_name or "").strip().lower()

    if tool_name == "knowledge":
        base_message = _extract_text_from_tool_data(
            tool_data,
            "Here is the information you asked for.",
        )
        return generate_agent_reply(
            task=(
                "Present this explanation in a natural and helpful way. "
                "If the content contains points, keep them clearly separated line by line. "
                "Do not greet. Do not make it sound like a textbook. "
                "A short natural lead-in is okay, but keep the explanation structured and readable."
            ),
            context={
                "response_type": "knowledge",
                "tool_name": tool_name,
                "profile": profile,
                "tool_data": tool_data,
                "conversation_stage": "ongoing",
                "base_message": base_message,
                "fallback_message": base_message,
            },
        )

    if tool_name == "reminder":
        if isinstance(tool_data, dict):
            reminder_date = (
                tool_data.get("date")
                or tool_data.get("scheduled_for")
                or tool_data.get("reminder_date")
                or tool_data.get("event_date")
            )
            task_name = (
                tool_data.get("task")
                or tool_data.get("title")
                or tool_data.get("name")
                or "a tax reminder"
            )

            if reminder_date:
                base_message = (
                    f"I’ve created {task_name} for {reminder_date}. "
                    "That way you won’t miss the date."
                )
            else:
                base_message = (
                    "I’ve created a tax reminder for you, so that part is taken care of."
                )
        else:
            base_message = (
                "I’ve created a tax reminder for you, so that part is taken care of."
            )

        return generate_agent_reply(
            task=(
                "Rewrite this reminder confirmation so it sounds natural, human, and slightly fuller. "
                "Keep it as a short paragraph, not a bullet list."
            ),
            context={
                "response_type": "reminder",
                "tool_name": tool_name,
                "profile": profile,
                "tool_data": tool_data,
                "conversation_stage": "ongoing",
                "base_message": base_message,
                "fallback_message": base_message,
            },
        )

    if tool_name == "document":
        base_text = _extract_text_from_tool_data(
            tool_data,
            "Here is your tax document checklist."
        )
        base_message = (
            f"I’ve put together the main documents you should keep ready.\n{base_text}"
            if not base_text.startswith("I’ve") and not base_text.startswith("Here")
            else base_text
        )

        return generate_agent_reply(
            task=(
                "Rewrite this document checklist response so it sounds natural and helpful. "
                "You can use a short conversational lead-in, but keep the actual checklist in bullet points or separate lines."
            ),
            context={
                "response_type": "documents",
                "tool_name": tool_name,
                "profile": profile,
                "tool_data": tool_data,
                "conversation_stage": "ongoing",
                "base_message": base_message,
                "fallback_message": base_message,
            },
        )

    if tool_name == "investment":
        base_text = _extract_text_from_tool_data(
            tool_data,
            "Here are some tax-saving investment suggestions for you."
        )
        if base_text.startswith("-"):
            base_message = (
                "Based on what you’ve shared, these are some tax-saving options worth considering:\n"
                f"{base_text}"
            )
        else:
            base_message = base_text

        return generate_agent_reply(
            task=(
                "Rewrite these investment suggestions so they sound natural, practical, and human. "
                "A short lead-in is fine, but keep the actual suggestions clearly separated in points or numbered lines."
            ),
            context={
                "response_type": "investment",
                "tool_name": tool_name,
                "profile": profile,
                "tool_data": tool_data,
                "conversation_stage": "ongoing",
                "base_message": base_message,
                "fallback_message": base_message,
            },
        )

    base_message = _extract_text_from_tool_data(tool_data, "Here is the result.")

    return generate_agent_reply(
        task=(
            "Rewrite this assistant response so it sounds natural, human, and slightly fuller. "
            "Keep the format appropriate to the content. "
            "Normal conversation should stay in paragraph form."
        ),
        context={
            "response_type": "general_tool",
            "tool_name": tool_name,
            "profile": profile,
            "tool_data": tool_data,
            "conversation_stage": "ongoing",
            "base_message": base_message,
            "fallback_message": base_message,
        },
    )