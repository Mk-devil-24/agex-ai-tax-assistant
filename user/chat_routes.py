from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from user.auth_utils import get_current_user_id_from_token
from user.chat_store import (
    create_chat,
    update_chat,
    delete_chat,
    list_user_chats,
    get_chat_by_id,
)

router = APIRouter()


class SaveChatRequest(BaseModel):
    token: str
    chat_id: str | None = None
    title: str
    messages: list
    summary: dict | None = None


def get_current_user_id(token: str):
    print("Received token:", token)
    user_id = get_current_user_id_from_token(token)

    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    return user_id


@router.post("/save")
def save_chat(request: SaveChatRequest):
    user_id = get_current_user_id(request.token)

    if request.chat_id:
        existing_chat = get_chat_by_id(request.chat_id)

        if not existing_chat:
            raise HTTPException(status_code=404, detail="Chat not found")

        if existing_chat["user_id"] != user_id:
            raise HTTPException(status_code=403, detail="Not allowed to update this chat")

        chat = update_chat(
            chat_id=request.chat_id,
            title=request.title,
            messages=request.messages,
            summary=request.summary,
        )
    else:
        chat = create_chat(
            user_id=user_id,
            title=request.title,
            messages=request.messages,
            summary=request.summary,
        )

    return {
        "status": "success",
        "message": "Chat saved successfully",
        "chat": chat,
    }


@router.get("/list")
def get_my_chats(token: str = Query(...)):
    user_id = get_current_user_id(token)
    chats = list_user_chats(user_id)

    return {
        "status": "success",
        "chats": chats,
    }


@router.get("/{chat_id}")
def get_chat(chat_id: str, token: str = Query(...)):
    user_id = get_current_user_id(token)
    chat = get_chat_by_id(chat_id)

    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")

    if chat["user_id"] != user_id:
        raise HTTPException(status_code=403, detail="Not allowed to access this chat")

    return {
        "status": "success",
        "chat": chat,
    }


@router.delete("/{chat_id}")
def remove_chat(chat_id: str, token: str = Query(...)):
    user_id = get_current_user_id(token)
    chat = get_chat_by_id(chat_id)

    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")

    if chat["user_id"] != user_id:
        raise HTTPException(status_code=403, detail="Not allowed to delete this chat")

    delete_chat(chat_id)

    return {
        "status": "success",
        "message": "Chat deleted successfully",
    }