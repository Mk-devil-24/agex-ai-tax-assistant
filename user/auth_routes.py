from fastapi import APIRouter, HTTPException
from user.auth_models import RegisterRequest, LoginRequest
from user.auth_utils import hash_password, verify_password, create_access_token
from user.auth_store import get_user_by_email, create_user

router = APIRouter()


@router.post("/register")
def register_user(request: RegisterRequest):
    existing_user = get_user_by_email(request.email)

    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")

    password_hash = hash_password(request.password)

    user = create_user(
        name=request.name,
        email=request.email,
        password_hash=password_hash,
    )

    token = create_access_token({
        "sub": user["id"],
        "email": user["email"],
        "name": user["name"],
    })

    return {
        "status": "success",
        "message": "User registered successfully",
        "user": {
            "id": user["id"],
            "name": user["name"],
            "email": user["email"],
        },
        "access_token": token,
        "token_type": "bearer",
    }


@router.post("/login")
def login_user(request: LoginRequest):
    user = get_user_by_email(request.email)

    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    if not verify_password(request.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_access_token({
        "sub": user["id"],
        "email": user["email"],
        "name": user["name"],
    })

    return {
        "status": "success",
        "message": "Login successful",
        "user": {
            "id": user["id"],
            "name": user["name"],
            "email": user["email"],
        },
        "access_token": token,
        "token_type": "bearer",
    }