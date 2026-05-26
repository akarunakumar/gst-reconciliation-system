from fastapi import APIRouter, HTTPException, status

from app.schemas.auth import LoginRequest, MessageResponse, RefreshRequest, TokenResponse
from app.services.auth_service import login, refresh_tokens

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=TokenResponse)
def auth_login(body: LoginRequest):
    tokens = login(body.username, body.password)
    if not tokens:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )
    return TokenResponse(
        access_token=tokens.access_token,
        refresh_token=tokens.refresh_token,
        username=tokens.username,
        role=tokens.role,
    )


@router.post("/logout", response_model=MessageResponse)
def auth_logout():
    # Stateless JWT — client discards the token. Phase 5 can add a denylist.
    return MessageResponse(message="Logged out successfully")


@router.post("/refresh", response_model=TokenResponse)
def auth_refresh(body: RefreshRequest):
    tokens = refresh_tokens(body.refresh_token)
    if not tokens:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )
    return TokenResponse(
        access_token=tokens.access_token,
        refresh_token=tokens.refresh_token,
        username=tokens.username,
        role=tokens.role,
    )
