"""
Auth API – login JWT. Mock temporaneo: solo admin/admin.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.core.security import create_access_token

router = APIRouter(prefix="/auth", tags=["auth"])


class LoginRequest(BaseModel):
    """Body POST /auth/login."""

    username: str
    password: str


class TokenResponse(BaseModel):
    """Risposta login: access_token e token_type."""

    access_token: str
    token_type: str = "bearer"


# Mock temporaneo: nessun DB utenti.
MOCK_USER = "admin"
MOCK_PASS = "admin"


@router.post("/login", response_model=TokenResponse)
def login(body: LoginRequest) -> TokenResponse:
    """
    Login: username e password. Restituisce JWT.
    Mock: accetta solo admin/admin.
    """
    if body.username != MOCK_USER or body.password != MOCK_PASS:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    token = create_access_token(user_id=body.username)
    return TokenResponse(access_token=token, token_type="bearer")
