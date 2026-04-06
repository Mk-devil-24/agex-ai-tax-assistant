import uuid

sessions = {}


def create_session(initial_query: str, profile: dict) -> str:
    session_id = str(uuid.uuid4())

    sessions[session_id] = {
        "initial_query": initial_query,
        "profile": profile,
        "followup_answers": [],
    }

    return session_id


def get_session(session_id: str) -> dict | None:
    return sessions.get(session_id)


def update_session(session_id: str, profile: dict, answer: str):
    if session_id in sessions:
        sessions[session_id]["profile"] = profile
        sessions[session_id]["followup_answers"].append(answer)


def delete_session(session_id: str):
    if session_id in sessions:
        del sessions[session_id]


