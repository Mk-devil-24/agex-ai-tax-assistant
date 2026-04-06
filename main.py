import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from user.auth_routes import router as auth_router
from user.chat_routes import router as chat_router
from agents.coordinator_agent import start_agex_flow, continue_agex_flow

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/api/auth", tags=["auth"])
app.include_router(chat_router, prefix="/api/chats", tags=["chats"])


class AnalyzeRequest(BaseModel):
    user_query: str


class FollowupRequest(BaseModel):
    session_id: str
    user_answer: str


@app.get("/api/health")
def health():
    return {"message": "AGEX API is running"}


@app.post("/api/analyze")
def analyze(request: dict):
    user_query = request.get("user_query")
    session_id = request.get("session_id") or request.get("sessionId")

    print("Incoming Request:", request)

    if session_id:
        print("Continuing session:", session_id)
        return continue_agex_flow(session_id, user_query)

    print("Starting new session")
    return start_agex_flow(user_query)


@app.post("/api/followup")
def followup(request: FollowupRequest):
    return continue_agex_flow(request.session_id, request.user_answer)


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIST = os.path.join(BASE_DIR, "frontend", "dist")
ASSETS_DIR = os.path.join(FRONTEND_DIST, "assets")

if os.path.exists(ASSETS_DIR):
    app.mount("/assets", StaticFiles(directory=ASSETS_DIR), name="assets")


@app.get("/favicon.ico", include_in_schema=False)
def favicon():
    favicon_path = os.path.join(FRONTEND_DIST, "favicon.ico")
    if os.path.exists(favicon_path):
        return FileResponse(favicon_path)
    return {"detail": "No favicon found"}


@app.get("/{full_path:path}", include_in_schema=False)
def serve_frontend(full_path: str):
    index_path = os.path.join(FRONTEND_DIST, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"detail": "Frontend not built. Run: cd frontend && npm run build"}