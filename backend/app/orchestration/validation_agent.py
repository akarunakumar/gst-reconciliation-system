from app.orchestration.base_agent import AgentResult, BaseAgent
from app.utils.column_detector import detect_columns
from app.utils.gstin_validator import validate_gstin


class ValidationAgent(BaseAgent):
    """Validates row-level data — warnings only, never blocks the upload."""

    def run(self, context: dict) -> AgentResult:
        rows: list[dict] = context.get("rows", [])
        warnings: list[str] = []
        seen_invoices: set[str] = set()

        if not rows:
            return AgentResult(success=True, data={"rows": rows, "warnings": ["File has no data rows"]})

        col_map = detect_columns(rows)
        inv_col = col_map.invoice_number
        gstin_col = col_map.gstin

        if not inv_col:
            warnings.append("Could not detect an invoice number column — reconciliation will use all columns for matching")
        if not gstin_col:
            warnings.append("Could not detect a GSTIN column — GSTIN-based matching will be skipped")

        for i, row in enumerate(rows, start=2):
            if inv_col:
                inv_num = str(row.get(inv_col) or "").strip()
                if inv_num and inv_num in seen_invoices:
                    warnings.append(f"Row {i}: duplicate invoice number '{inv_num}'")
                if inv_num:
                    seen_invoices.add(inv_num)

            if gstin_col:
                gstin = str(row.get(gstin_col) or "").strip()
                if gstin and not validate_gstin(gstin):
                    warnings.append(f"Row {i}: non-standard GSTIN format '{gstin}'")

        return AgentResult(success=True, data={"rows": rows, "warnings": warnings})
