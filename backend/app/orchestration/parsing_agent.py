from app.orchestration.base_agent import AgentResult, BaseAgent
from app.utils.excel_parser import parse_gstr2b_excel, parse_invoice_excel


class ExcelParsingAgent(BaseAgent):
    """Parses Excel bytes into list[dict] rows based on file_type in context."""

    def run(self, context: dict) -> AgentResult:
        file_bytes: bytes = context.get("file_bytes", b"")
        file_type: str = context.get("file_type", "invoice")

        try:
            rows = parse_invoice_excel(file_bytes) if file_type == "invoice" else parse_gstr2b_excel(file_bytes)
            return AgentResult(success=True, data={"rows": rows, "row_count": len(rows)})
        except ValueError as exc:
            return AgentResult(success=False, errors=[str(exc)])
        except Exception as exc:
            return AgentResult(success=False, errors=[f"Failed to parse Excel file: {exc}"])
