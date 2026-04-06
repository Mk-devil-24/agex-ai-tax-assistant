from datetime import datetime
from google.cloud import firestore

PROJECT_ID = "agex-hackathon"
DATABASE_ID = "agex-hackathon"

db = firestore.Client(project=PROJECT_ID, database=DATABASE_ID)


def create_chat(user_id: str, title: str, messages: list, summary: dict | None = None):
    doc_ref = db.collection("saved_chats").document()
    chat_data = {
        "user_id": user_id,
        "title": title,
        "messages": messages,
        "summary": summary or {},
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
    }
    doc_ref.set(chat_data)
    chat_data["id"] = doc_ref.id
    return chat_data


def update_chat(chat_id: str, title: str, messages: list, summary: dict | None = None):
    doc_ref = db.collection("saved_chats").document(chat_id)
    doc_ref.update({
        "title": title,
        "messages": messages,
        "summary": summary or {},
        "updated_at": datetime.utcnow().isoformat(),
    })
    doc = doc_ref.get()
    data = doc.to_dict()
    data["id"] = doc.id
    return data


def delete_chat(chat_id: str):
    db.collection("saved_chats").document(chat_id).delete()


def list_user_chats(user_id: str):
    docs = db.collection("saved_chats").where("user_id", "==", user_id).stream()

    chats = []
    for doc in docs:
        data = doc.to_dict()
        data["id"] = doc.id
        chats.append(data)

    chats.sort(key=lambda x: x.get("updated_at", ""), reverse=True)
    return chats


def get_chat_by_id(chat_id: str):
    doc = db.collection("saved_chats").document(chat_id).get()
    if not doc.exists:
        return None

    data = doc.to_dict()
    data["id"] = doc.id
    return data