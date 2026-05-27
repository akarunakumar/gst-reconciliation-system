from app.orchestration.base_agent import AgentResult, BaseAgent
from app.utils.excel_parser import parse_excel


class ExcelParsingAgent(BaseAgent):
    """Parses Excel bytes into list[dict] rows regardless of file type (invoice or GSTR2B)."""

    def run(self, context: dict) -> AgentResult:
        file_bytes: bytes = context.get("file_bytes", b"")

        try:
            rows = parse_excel(file_bytes)
            return AgentResult(success=True, data={"rows": rows, "row_count": len(rows)})
        except ValueError as exc:
            return AgentResult(success=False, errors=[str(exc)])
        except Exception as exc:
            return AgentResult(success=False, errors=[f"Failed to parse Excel file: {exc}"])
