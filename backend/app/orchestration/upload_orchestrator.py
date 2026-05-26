import logging

from app.orchestration.base_agent import AgentResult
from app.orchestration.parsing_agent import ExcelParsingAgent
from app.orchestration.upload_agent import FileUploadAgent
from app.orchestration.validation_agent import ValidationAgent

logger = logging.getLogger(__name__)


class UploadOrchestrator:
    """Chains FileUploadAgent → ExcelParsingAgent → ValidationAgent."""

    def __init__(self) -> None:
        self._upload_agent = FileUploadAgent()
        self._parsing_agent = ExcelParsingAgent()
        self._validation_agent = ValidationAgent()

    def process(self, filename: str, file_bytes: bytes, file_type: str) -> AgentResult:
        context: dict = {"filename": filename, "file_bytes": file_bytes, "file_type": file_type}

        # Step 1: file type + size validation
        result = self._run_agent(self._upload_agent, context)
        if not result.success:
            return result
        context.update(result.data)

        # Step 2: Excel parsing
        result = self._run_agent(self._parsing_agent, context)
        if not result.success:
            return result
        context.update(result.data)

        # Step 3: row-level validation (retry once on unexpected error)
        result = self._run_with_retry(self._validation_agent, context)
        if not result.success:
            return result
        context.update(result.data)

        return AgentResult(
            success=True,
            data={
                "rows": context["rows"],
                "row_count": context["row_count"],
                "warnings": context.get("warnings", []),
            },
        )

    def _run_agent(self, agent, context: dict) -> AgentResult:
        logger.info("[%s] starting", agent.name)
        result = agent.run(context)
        if result.success:
            logger.info("[%s] completed — rows=%s", agent.name, result.data.get("row_count", "n/a"))
        else:
            logger.warning("[%s] failed — %s", agent.name, result.errors)
        return result

    def _run_with_retry(self, agent, context: dict, retries: int = 1) -> AgentResult:
        for attempt in range(retries + 1):
            result = self._run_agent(agent, context)
            if result.success or attempt == retries:
                return result
            logger.warning("[%s] retrying (attempt %d)", agent.name, attempt + 1)
        return result  # type: ignore[return-value]
