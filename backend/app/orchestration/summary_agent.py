from app.orchestration.base_agent import AgentResult, BaseAgent
from app.utils.amount_parser import parse_amount
from app.utils.column_detector import ColumnMap


class SummaryGenerationAgent(BaseAgent):
    def run(self, context: dict) -> AgentResult:
        matched: list[dict] = context.get("matched_records", [])
        unmatched: list[dict] = context.get("unmatched_records", [])
        invoice_rows: list[dict] = context.get("invoice_rows", [])
        gstr2b_rows: list[dict] = context.get("gstr2b_rows", [])
        inv_map: ColumnMap = context["invoice_col_map"]
        g2b_map: ColumnMap = context["gstr2b_col_map"]

        matched_count = len(matched)
        amount_mismatch = sum(1 for r in unmatched if "Amount mismatch" in r.get("mismatch_reason", ""))
        gstin_mismatch = sum(1 for r in unmatched if "GSTIN mismatch" in r.get("mismatch_reason", ""))
        only_in_invoice = sum(1 for r in unmatched if r.get("missing_source") == "GSTR2B")
        only_in_gstr2b = sum(1 for r in unmatched if r.get("missing_source") == "INVOICE")

        total_inv = len(invoice_rows)
        match_pct = round((matched_count / total_inv * 100), 2) if total_inv else 0.0

        total_taxable_inv = sum(parse_amount(r, inv_map.taxable_amount) for r in invoice_rows)
        total_taxable_g2b = sum(parse_amount(r, g2b_map.taxable_amount) for r in gstr2b_rows)

        return AgentResult(success=True, data={
            "summary": {
                "total_invoice_records": total_inv,
                "total_gstr2b_records": len(gstr2b_rows),
                "matched_count": matched_count,
                "amount_mismatch_count": amount_mismatch,
                "gstin_mismatch_count": gstin_mismatch,
                "only_in_invoice_count": only_in_invoice,
                "only_in_gstr2b_count": only_in_gstr2b,
                "match_percentage": match_pct,
                "total_taxable_invoice": round(total_taxable_inv, 2),
                "total_taxable_gstr2b": round(total_taxable_g2b, 2),
                "taxable_difference": round(abs(total_taxable_inv - total_taxable_g2b), 2),
            }
        })
