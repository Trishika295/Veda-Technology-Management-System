from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, status, Depends
from app.database import get_db, record_activity, serialize_doc
from app.schemas import UserRegister, UserLogin, UserResponse, TokenResponse
from app.services import (
    hash_password,
    verify_password,
    create_access_token,
    require_auth_user,
    generate_entity_id,
    PREFIX_USER
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: UserRegister):
    db = get_db()
    existing = db.users.find_one({"email": user_data.email.lower()})
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email address already exists."
        )

    user_id = generate_entity_id("users", PREFIX_USER)
    new_user = {
        "user_id": user_id,
        "name": user_data.name.strip(),
        "email": user_data.email.lower().strip(),
        "password_hash": hash_password(user_data.password),
        "role": user_data.role or "Staff",
        "created_at": datetime.now(timezone.utc)
    }
    result = db.users.insert_one(new_user)
    new_user["_id"] = result.inserted_id

    serialized = serialize_doc(new_user)
    token = create_access_token(data={"sub": serialized["email"], "role": serialized["role"]})

    record_activity("REGISTER", "Auth", f"User registered: {serialized['name']} ({serialized['email']})", user_id, serialized["email"])

    return {
        "access_token": token,
        "token_type": "bearer",
        "user": serialized
    }


@router.post("/login", response_model=TokenResponse)
def login(credentials: UserLogin):
    db = get_db()
    user = db.users.find_one({"email": credentials.email.lower().strip()})
    if not user or not verify_password(credentials.password, user.get("password_hash", "")):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password. Please try again."
        )

    serialized = serialize_doc(user)
    token = create_access_token(data={"sub": serialized["email"], "role": serialized.get("role", "Staff")})

    record_activity("LOGIN", "Auth", f"User logged in: {serialized['email']}", serialized.get("user_id"), serialized["email"])

    return {
        "access_token": token,
        "token_type": "bearer",
        "user": serialized
    }


@router.get("/me", response_model=UserResponse)
def get_current_user(current_user: dict = Depends(require_auth_user)):
    return current_user
