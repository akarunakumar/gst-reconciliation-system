from dataclasses import dataclass

from app.utils.password import hash_password, verify_password


@dataclass
class UserRecord:
    id: int
    username: str
    password_hash: str
    role: str


class MockUserRepository:
    """In-memory user store. Swap for DBUserRepository when USE_MOCK_SERVICES=false."""

    _users: dict[str, UserRecord] = {
        "admin": UserRecord(1, "admin", hash_password("Admin@123"), "admin"),
        "auditor": UserRecord(2, "auditor", hash_password("Audit@123"), "auditor"),
        "viewer": UserRecord(3, "viewer", hash_password("View@123"), "viewer"),
    }

    def get_by_username(self, username: str) -> UserRecord | None:
        return self._users.get(username)

    def verify_credentials(self, username: str, password: str) -> UserRecord | None:
        user = self.get_by_username(username)
        if user and verify_password(password, user.password_hash):
            return user
        return None
