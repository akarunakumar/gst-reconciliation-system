from app.orchestration.base_agent import AgentResult
from app.orchestration.upload_orchestrator import UploadOrchestrator
from app.repositories.session_repository import MockSessionRepository, ReconciliationSession, get_session_repository

_orchestrator = UploadOrchestrator()


def handle_upload(filename: str, file_bytes: bytes, file_type: str) -> AgentResult:
    """Run the upload orchestration pipeline and store parsed rows in temp store."""
    result = _orchestrator.process(filename, file_bytes, file_type)
    if not result.success:
        return result

    repo: MockSessionRepository = get_session_repository()
    temp_key = repo.store_temp(result.data["rows"], filename, file_type)
    result.data["temp_key"] = temp_key
    return result


def create_session(
    invoice_temp_key: str,
    gstr2b_temp_key: str,
    session_name: str = "",
) -> ReconciliationSession | None:
    repo = get_session_repository()
    return repo.create_session(invoice_temp_key, gstr2b_temp_key, session_name)
