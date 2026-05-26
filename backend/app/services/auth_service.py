from dataclasses import dataclass

from app.core.config import settings
from app.core.security import create_access_token, create_refresh_token, verify_refresh_token
from app.repositories.user_repository import MockUserRepository, UserRecord


@dataclass
class TokenPair:
    access_token: str
    refresh_token: str
    username: str
    role: str


def _get_repository() -> MockUserRepository:
    # Phase 2: swap for DBUserRepository when settings.USE_MOCK_SERVICES is False
    return MockUserRepository()


def authenticate_user(username: str, password: str) -> UserRecord | None:
    repo = _get_repository()
    return repo.verify_credentials(username, password)


def login(username: str, password: str) -> TokenPair | None:
    user = authenticate_user(username, password)
    if not user:
        return None
    payload = {"sub": user.username, "role": user.role, "user_id": user.id}
    return TokenPair(
        access_token=create_access_token(payload),
        refresh_token=create_refresh_token(payload),
        username=user.username,
        role=user.role,
    )


def refresh_tokens(refresh_token: str) -> TokenPair | None:
    try:
        payload = verify_refresh_token(refresh_token)
    except Exception:
        return None

    repo = _get_repository()
    user = repo.get_by_username(payload.get("sub", ""))
    if not user:
        return None

    new_payload = {"sub": user.username, "role": user.role, "user_id": user.id}
    return TokenPair(
        access_token=create_access_token(new_payload),
        refresh_token=create_refresh_token(new_payload),
        username=user.username,
        role=user.role,
    )
