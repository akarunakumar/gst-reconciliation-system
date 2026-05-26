import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class ReconciliationSession:
    id: str
    session_name: str
    invoice_filename: str
    gstr2b_filename: str
    invoice_rows: list[dict]
    gstr2b_rows: list[dict]
    status: str  # "uploaded" | "processing" | "completed" | "error"
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    matched_records: list[dict] = field(default_factory=list)
    unmatched_records: list[dict] = field(default_factory=list)
    summary: dict = field(default_factory=dict)


class MockSessionRepository:
    """In-memory session store. Replace with DBSessionRepository when USE_MOCK_SERVICES=false."""

    _sessions: dict[str, ReconciliationSession] = {}
    _temp_store: dict[str, dict] = {}  # key → {rows, filename, file_type}

    def store_temp(self, rows: list[dict], filename: str, file_type: str) -> str:
        key = str(uuid.uuid4())
        self._temp_store[key] = {"rows": rows, "filename": filename, "file_type": file_type}
        return key

    def get_temp(self, key: str) -> dict | None:
        return self._temp_store.get(key)

    def create_session(
        self,
        invoice_key: str,
        gstr2b_key: str,
        session_name: str = "",
    ) -> ReconciliationSession | None:
        inv = self.get_temp(invoice_key)
        g2b = self.get_temp(gstr2b_key)
        if not inv or not g2b:
            return None
        session = ReconciliationSession(
            id=str(uuid.uuid4()),
            session_name=session_name or f"Session {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M')}",
            invoice_filename=inv["filename"],
            gstr2b_filename=g2b["filename"],
            invoice_rows=inv["rows"],
            gstr2b_rows=g2b["rows"],
            status="uploaded",
        )
        self._sessions[session.id] = session
        return session

    def get(self, session_id: str) -> ReconciliationSession | None:
        return self._sessions.get(session_id)

    def update_results(self, session_id: str, matched: list[dict], unmatched: list[dict], summary: dict) -> None:
        session = self._sessions.get(session_id)
        if session:
            session.matched_records = matched
            session.unmatched_records = unmatched
            session.summary = summary
            session.status = "completed"

    def list_all(self) -> list[ReconciliationSession]:
        return list(self._sessions.values())


_repo = MockSessionRepository()


def get_session_repository() -> MockSessionRepository:
    return _repo
