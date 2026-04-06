from agents.profile_agent import (
    extract_profile_details_with_fallback,
    generate_followup_question,
)

from agents.tax_agent import fetch_tax_rules
from agents.recommendation_agent import generate_recommendations_with_gemini
from agents.task_agent import generate_tasks_with_fallback
from agents.document_agent import generate_documents_with_fallback
from agents.storage_agent import save_workflow_log
from agents.session_agent import create_session, get_session, update_session

from agents.intent_agent import classify_intent
from agents.conversation_agent import (
    handle_general_conversation,
    make_followup_conversational,
    make_completion_summary,
    make_tool_response_conversational,
)

from agents.tools.investment_tool_client import get_investment_suggestions
from agents.tools.document_tool_client import get_document_checklist
from agents.tools.calendar_tool_client import create_tax_reminder
from agents.tools.knowledge_tool_client import search_knowledge
from agents.formatter.knowledge_formatter import format_knowledge_response


GENERAL_INTENTS = {
    "greeting",
    "wellbeing",
    "introduction",
    "capabilities",
    "gratitude",
    "acknowledgement",
    "off_topic",
    "general",
    "goodbye",
}

TOOL_INTENTS = {
    "knowledge",
    "investment",
    "document",
    "reminder",
    "explanation",
    "reminder_tool",
    "document_tool",
    "investment_tool",
    "knowledge_tool",
}

TOOL_INTENT_MAP = {
    "reminder_tool": "reminder",
    "document_tool": "document",
    "investment_tool": "investment",
    "knowledge_tool": "knowledge",
}


def log(label, data=None):
    print(f"\n🔹 {label}")
    if data is not None:
        print(data)


def empty_result():
    return {
        "summary": {},
        "tax_rules_considered": [],
        "recommendations": [],
        "investment_suggestions": {},
        "action_tasks": [],
        "document_checklist": [],
        "document_checklist_mcp": {},
        "calendar_reminder": {},
    }


def safe_tool_call(fn, *args, **kwargs):
    try:
        return fn(*args, **kwargs)
    except Exception as e:
        print("❌ TOOL ERROR:", str(e))
        return {"error": str(e)}


def normalize_intent(intent: str) -> str:
    intent = (intent or "").strip().lower()
    return TOOL_INTENT_MAP.get(intent, intent)


def parse_yes_no(answer: str):
    text = (answer or "").lower().strip()

    positive_phrases = [
        "yes",
        "yes i do",
        "i do",
        "yeah",
        "yep",
        "yup",
        "of course",
        "sure",
        "haan",
        "ha",
        "ji",
    ]

    negative_phrases = [
        "no",
        "nope",
        "nah",
        "not really",
        "i don't",
        "i dont",
        "don't",
        "dont",
        "none",
        "no investments",
    ]

    for phrase in positive_phrases:
        if phrase in text:
            return True

    for phrase in negative_phrases:
        if phrase in text:
            return False

    return None


def extract_text_from_tool_result(data, fallback_message="Here is the information you asked for."):
    if data is None:
        return fallback_message

    if isinstance(data, str):
        cleaned = data.strip()
        return cleaned if cleaned else fallback_message

    if isinstance(data, dict):
        for key in [
            "answer",
            "result",
            "message",
            "content",
            "text",
            "response",
            "summary",
            "details",
        ]:
            value = data.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()

        if "suggestions" in data and isinstance(data["suggestions"], list) and data["suggestions"]:
            return "\n".join(f"- {item}" for item in data["suggestions"])

        if "documents" in data and isinstance(data["documents"], list) and data["documents"]:
            return "\n".join(f"- {item}" for item in data["documents"])

        return str(data)

    if isinstance(data, list):
        if not data:
            return fallback_message
        return "\n".join(str(item) for item in data)

    return str(data)


def detect_direct_tool_from_query(user_query: str):
    q = (user_query or "").lower().strip()

    knowledge_keywords = [
        "what is",
        "meaning of",
        "explain",
        "pf",
        "epf",
        "ppf",
        "elss",
        "nps",
        "80c",
        "hra",
        "lta",
        "itr",
        "tax regime",
    ]

    investment_keywords = [
        "where can i invest",
        "where should i invest",
        "how can i invest",
        "investment options",
        "save tax investment",
        "tax saving investment",
        "tax-saving investment",
        "where to invest",
        "invest to save tax",
        "tax saver options",
    ]

    document_keywords = [
        "what documents do i need",
        "documents do i need",
        "document checklist",
        "documents required",
        "what proof do i need",
        "which documents",
    ]

    reminder_keywords = [
        "set reminder",
        "create reminder",
        "remind me",
        "set a reminder",
    ]

    if any(keyword in q for keyword in reminder_keywords):
        return "reminder"

    if any(keyword in q for keyword in document_keywords):
        return "document"

    if any(keyword in q for keyword in investment_keywords):
        return "investment"

    if any(keyword in q for keyword in knowledge_keywords):
        return "knowledge"

    return None


def route_explanation_intent(intent: str, user_query: str) -> str:
    intent = normalize_intent(intent)

    forced_tool = detect_direct_tool_from_query(user_query)
    if forced_tool:
        log("➡️ Direct tool route matched", forced_tool)
        return forced_tool

    if intent != "explanation":
        return intent

    log("🧠 Explanation detected - routing check", user_query)
    q = (user_query or "").lower()

    investment_keywords = [
        "pf",
        "epf",
        "ppf",
        "elss",
        "nps",
        "80c",
        "tax saving",
        "tax saver",
        "deduction",
        "regime",
        "hra",
        "lta",
        "it return",
        "itr",
    ]

    if any(word in q for word in investment_keywords):
        log("➡️ Routed to KNOWLEDGE tool")
        return "knowledge"

    log("➡️ No keyword match, staying as explanation")
    return "explanation"


def get_pending_field(profile: dict):
    log("Checking pending field", profile)

    if profile.get("persona") is None:
        return "persona"

    if profile.get("persona") == "salaried":
        if profile.get("rent_paid") is None:
            return "rent_paid"
        if profile.get("has_investments") is None:
            return "has_investments"

    if profile.get("persona") in ["business", "small_business"]:
        if profile.get("has_gst_concern") is None:
            return "has_gst_concern"

    return None


def apply_followup_answer(profile: dict, answer: str, pending_field):
    text = (answer or "").lower().strip()
    updated = profile.copy()

    log(
        "Applying followup answer",
        {
            "pending_field": pending_field,
            "answer": text,
            "before": profile,
        },
    )

    yn_value = parse_yes_no(text)

    if pending_field == "persona":
        if "salary" in text or "salaried" in text:
            updated["persona"] = "salaried"
        elif "business" in text or "self employed" in text or "self-employed" in text:
            updated["persona"] = "business"

    elif pending_field == "rent_paid":
        if yn_value is not None:
            updated["rent_paid"] = yn_value

    elif pending_field == "has_investments":
        if yn_value is not None:
            updated["has_investments"] = yn_value
        else:
            investment_keywords = ["pf", "epf", "ppf", "elss", "nps", "insurance", "fd", "mutual fund"]
            if any(word in text for word in investment_keywords):
                updated["has_investments"] = True

    elif pending_field == "has_gst_concern":
        if yn_value is not None:
            updated["has_gst_concern"] = yn_value

    log("Updated profile after followup", updated)
    return updated


def process_profile(profile, user_input):
    log("Processing profile with input", user_input)

    extracted = extract_profile_details_with_fallback(user_input)
    log("Extracted profile", extracted)

    for key, value in extracted.items():
        if profile.get(key) is None and value is not None:
            profile[key] = value

    log("Profile after safe merge", profile)

    followup = generate_followup_question(profile)
    log("Generated followup", followup)

    return profile, followup

def handle_tool(intent, user_query, profile=None):
    intent = normalize_intent(intent)
    log("🧰 TOOL EXECUTION START", intent)

    profile = profile or {}
    log("Handling tool", intent)

    if intent in ["knowledge", "explanation"]:
        log("📘 Calling KNOWLEDGE tool")
        data = safe_tool_call(search_knowledge, user_query)

        if isinstance(data, dict) and (data.get("error") or data.get("status") == "error"):
            log("❌ Knowledge tool failed", data)
            result = empty_result()
            result.update(
                {
                    "status": "error",
                    "message": "Sorry, I couldn’t fetch that information right now.",
                }
            )
            return result

        knowledge_text = format_knowledge_response(data)

        

        result = empty_result()
        result.update(
            {
                "status": "answer",
                "message": knowledge_text,
            }
        )
        return result

    if intent == "investment":
        log("💰 Calling INVESTMENT tool")
        data = safe_tool_call(
            get_investment_suggestions,
            persona=profile.get("persona", "salaried"),
            income=800000,
        )

        message = make_tool_response_conversational("investment", data, profile)

        result = empty_result()
        result.update(
            {
                "status": "answer",
                "message": message,
                "summary": profile,
                "investment_suggestions": data,
            }
        )
        return result

    if intent == "document":
        log("📄 Calling DOCUMENT tool")
        data = safe_tool_call(
            get_document_checklist,
            persona=profile.get("persona", "salaried"),
            rent_paid=profile.get("rent_paid", False),
            investments=profile.get("has_investments", False),
        )

        message = make_tool_response_conversational("document", data, profile)

        result = empty_result()
        result.update(
            {
                "status": "answer",
                "message": message,
                "summary": profile,
                "document_checklist_mcp": data,
            }
        )
        return result

    if intent == "reminder":
        log("⏰ Calling REMINDER tool")
        default_date = "2026-07-31"

        data = safe_tool_call(
            create_tax_reminder,
            task="File Income Tax Return",
            date=default_date,
        )

        if isinstance(data, dict) and data.get("error"):
            result = empty_result()
            result.update(
                {
                    "status": "error",
                    "message": "Sorry, I couldn’t create the tax reminder right now.",
                    "summary": profile,
                    "calendar_reminder": data,
                }
            )
            return result

        message = make_tool_response_conversational("reminder", data, profile)

        result = empty_result()
        result.update(
            {
                "status": "answer",
                "message": message,
                "summary": profile,
                "calendar_reminder": data,
            }
        )
        return result

    log("❌ No matching tool found for intent", intent)
    result = empty_result()
    result.update(
        {
            "status": "error",
            "message": "No valid tool matched",
        }
    )
    return result

def complete_workflow(profile, user_query, session_id=None):
    log("🚀 Completing workflow", profile)

    persona = profile.get("persona", "salaried")

    rules = safe_tool_call(fetch_tax_rules, persona)
    recommendations = safe_tool_call(generate_recommendations_with_gemini, profile)
    tasks = safe_tool_call(generate_tasks_with_fallback, profile)
    documents = safe_tool_call(generate_documents_with_fallback, profile)

    save_workflow_log(
        user_query=user_query,
        profile=profile,
        recommendations=recommendations,
        tasks=tasks,
        documents=documents,
    )

    if session_id:
        completed_profile = profile.copy()
        completed_profile.pop("_pending_field", None)
        update_session(session_id, completed_profile, "complete")

    return {
        "status": "complete",
        "message": make_completion_summary(profile),
        "summary": profile,
        "tax_rules_considered": rules,
        "recommendations": recommendations,
        "investment_suggestions": {},
        "action_tasks": tasks,
        "document_checklist": documents,
        "document_checklist_mcp": {},
        "calendar_reminder": {},
    }


def start_agex_flow(user_query: str):
    log("🟢 START FLOW", user_query)

    intent = classify_intent(user_query)
    intent = normalize_intent(intent)
    intent = route_explanation_intent(intent, user_query)

    log("Detected intent", intent)

    if intent in GENERAL_INTENTS:
        res = handle_general_conversation(intent)
        res.update(empty_result())
        return res

    if intent in TOOL_INTENTS:
        log(
            "🛠 Tool intent check",
            {
                "intent": intent,
                "is_tool_intent": intent in TOOL_INTENTS,
                "query": user_query,
            },
        )
        return handle_tool(intent, user_query)

    if intent == "tax_workflow":
        profile = {}
        profile, followup = process_profile(profile, user_query)

        pending = get_pending_field(profile)
        log("Pending field", pending)

        if pending:
            profile["_pending_field"] = pending
            session_id = create_session(user_query, profile)

            log("Creating session", session_id)

            return {
                "status": "need_followup",
                "session_id": session_id,
                "profile": profile,
                "followup_question": make_followup_conversational(profile, followup),
            }

        return complete_workflow(profile, user_query)

    res = handle_general_conversation("general")
    res.update(empty_result())
    return res


def continue_agex_flow(session_id: str, user_answer: str):
    log("🟡 CONTINUE FLOW", {"session": session_id, "answer": user_answer})

    session = get_session(session_id)

    if not session:
        res = {"status": "error", "message": "Invalid session_id"}
        res.update(empty_result())
        return res

    profile = session.get("profile", {})
    pending = profile.get("_pending_field")

    log("Session profile", profile)
    log("Pending field", pending)

    intent = classify_intent(user_answer)
    intent = normalize_intent(intent)
    intent = route_explanation_intent(intent, user_answer)

    log("Detected intent (continue)", intent)

    if intent in TOOL_INTENTS:
        log(
            "🛠 (Continue) Tool intent check",
            {
                "intent": intent,
                "is_tool_intent": intent in TOOL_INTENTS,
                "query": user_answer,
            },
        )
        return handle_tool(intent, user_answer, profile)

    if pending:
        profile = apply_followup_answer(profile, user_answer, pending)
        profile.pop("_pending_field", None)

        profile, followup = process_profile(profile, user_answer)

        new_pending = get_pending_field(profile)
        log("New pending field", new_pending)

        if new_pending:
            profile["_pending_field"] = new_pending
            update_session(session_id, profile, user_answer)

            return {
                "status": "need_followup",
                "session_id": session_id,
                "profile": profile,
                "followup_question": make_followup_conversational(profile, followup),
            }

        return complete_workflow(profile, session.get("initial_query", user_answer), session_id)

    if intent == "tax_workflow":
        direct_tool = detect_direct_tool_from_query(user_answer)
        if direct_tool:
            log("➡️ Continuing session via direct tool after workflow completion", direct_tool)
            return handle_tool(direct_tool, user_answer, profile)

        updated_profile, followup = process_profile(profile.copy(), user_answer)
        new_pending = get_pending_field(updated_profile)

        if new_pending:
            updated_profile["_pending_field"] = new_pending
            update_session(session_id, updated_profile, user_answer)
            return {
                "status": "need_followup",
                "session_id": session_id,
                "profile": updated_profile,
                "followup_question": make_followup_conversational(updated_profile, followup),
            }

        return complete_workflow(updated_profile, session.get("initial_query", user_answer), session_id)

    if intent in GENERAL_INTENTS:
        res = handle_general_conversation(intent)
        res.update(empty_result())
        return res

    res = handle_general_conversation("general")
    res.update(empty_result())
    return res