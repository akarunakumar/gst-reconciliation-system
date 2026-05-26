from app.orchestration.reconciliation_orchestrator import ReconciliationOrchestrator
from app.repositories.session_repository import ReconciliationSession, get_session_repository

_orchestrator = ReconciliationOrchestrator()


def run_reconciliation(session_id: str) -> ReconciliationSession | None:
    repo = get_session_repository()
    session = repo.get(session_id)
    if not session:
        return None

    session.status = "processing"
    result = _orchestrator.process(session.invoice_rows, session.gstr2b_rows)

    if not result.success:
        session.status = "error"
        return session

    repo.update_results(
        session_id,
        matched=result.data["matched_records"],
        unmatched=result.data["unmatched_records"],
        summary=result.data["summary"],
    )
    return repo.get(session_id)


def get_session(session_id: str) -> ReconciliationSession | None:
    return get_session_repository().get(session_id)
