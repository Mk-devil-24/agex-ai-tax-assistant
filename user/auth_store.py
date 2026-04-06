from google.cloud import firestore

PROJECT_ID = "agex-hackathon"

db = firestore.Client(database="agex-hackathon")


def get_user_by_email(email: str):
    docs = db.collection("users").where("email", "==", email).limit(1).stream()
    for doc in docs:
        data = doc.to_dict()
        data["id"] = doc.id
        return data
    return None


def create_user(name: str, email: str, password_hash: str):
    doc_ref = db.collection("users").document()
    user_data = {
        "name": name,
        "email": email,
        "password_hash": password_hash,
    }
    doc_ref.set(user_data)
    user_data["id"] = doc_ref.id
    return user_data