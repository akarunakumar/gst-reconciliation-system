import logging
from app.orchestration.base_agent import AgentResult, BaseAgent
from app.utils.column_detector import ColumnMap

logger = logging.getLogger(__name__)

AMOUNT_TOLERANCE = 1.0  # ±₹1 rounding tolerance


def _val(row: dict, col: str | None) -> str:
    if not col:
        return ""
    return str(row.get(col) or "").strip()


def _amount(row: dict, col: str | None) -> float:
    if not col:
        return 0.0
    try:
        return float(str(row.get(col) or "0").replace(",", ""))
    except (ValueError, TypeError):
        return 0.0


def _norm_inv(val: str) -> str:
    return val.upper().replace(" ", "").replace("/", "").replace("-", "")


class GSTMatchingAgent(BaseAgent):
    """Matches invoice rows against GSTR2B rows using detected column maps."""

    def run(self, context: dict) -> AgentResult:
        invoice_rows: list[dict] = context.get("invoice_rows", [])
        gstr2b_rows: list[dict] = context.get("gstr2b_rows", [])
        inv_map: ColumnMap = context["invoice_col_map"]
        g2b_map: ColumnMap = context["gstr2b_col_map"]

        # Build GSTR2B lookup: normalised invoice_number → row
        g2b_lookup: dict[str, dict] = {}
        for row in gstr2b_rows:
            key = _norm_inv(_val(row, g2b_map.invoice_number))
            if key:
                g2b_lookup[key] = row

        matched: list[dict] = []
        unmatched: list[dict] = []
        consumed_g2b_keys: set[str] = set()

        for row in invoice_rows:
            inv_num = _val(row, inv_map.invoice_number)
            inv_key = _norm_inv(inv_num)
            inv_gstin = _val(row, inv_map.gstin)
            inv_vendor = _val(row, inv_map.vendor_name)
            inv_taxable = _amount(row, inv_map.taxable_amount)
            inv_igst = _amount(row, inv_map.igst)
            inv_cgst = _amount(row, inv_map.cgst)
            inv_sgst = _amount(row, inv_map.sgst)

            g2b_row = g2b_lookup.get(inv_key) if inv_key else None

            if g2b_row is None:
                unmatched.append({
                    "invoice_number": inv_num,
                    "gstin": inv_gstin,
                    "mismatch_reason": "Invoice not found in GSTR2B",
                    "missing_source": "GSTR2B",
                    "amount_difference": 0.0,
                    "raw_invoice": row,
                    "raw_gstr2b": None,
                })
                continue

            consumed_g2b_keys.add(inv_key)
            g2b_gstin = _val(g2b_row, g2b_map.gstin)
            g2b_taxable = _amount(g2b_row, g2b_map.taxable_amount)
            g2b_igst = _amount(g2b_row, g2b_map.igst)
            g2b_cgst = _amount(g2b_row, g2b_map.cgst)
            g2b_sgst = _amount(g2b_row, g2b_map.sgst)

            # GSTIN mismatch check
            if inv_gstin and g2b_gstin and inv_gstin.upper() != g2b_gstin.upper():
                unmatched.append({
                    "invoice_number": inv_num,
                    "gstin": inv_gstin,
                    "mismatch_reason": f"GSTIN mismatch: Invoice={inv_gstin} vs GSTR2B={g2b_gstin}",
                    "missing_source": "NONE",
                    "amount_difference": abs(inv_taxable - g2b_taxable),
                    "raw_invoice": row,
                    "raw_gstr2b": g2b_row,
                })
                continue

            # Amount mismatch check
            taxable_diff = abs(inv_taxable - g2b_taxable)
            igst_diff = abs(inv_igst - g2b_igst)
            cgst_diff = abs(inv_cgst - g2b_cgst)
            sgst_diff = abs(inv_sgst - g2b_sgst)
            total_diff = taxable_diff + igst_diff + cgst_diff + sgst_diff

            if total_diff > AMOUNT_TOLERANCE:
                reasons = []
                if taxable_diff > AMOUNT_TOLERANCE:
                    reasons.append(f"Taxable: ₹{inv_taxable} vs ₹{g2b_taxable} (diff ₹{taxable_diff:.2f})")
                if igst_diff > AMOUNT_TOLERANCE:
                    reasons.append(f"IGST: ₹{inv_igst} vs ₹{g2b_igst}")
                if cgst_diff > AMOUNT_TOLERANCE:
                    reasons.append(f"CGST: ₹{inv_cgst} vs ₹{g2b_cgst}")
                if sgst_diff > AMOUNT_TOLERANCE:
                    reasons.append(f"SGST: ₹{inv_sgst} vs ₹{g2b_sgst}")
                unmatched.append({
                    "invoice_number": inv_num,
                    "gstin": inv_gstin,
                    "mismatch_reason": "Amount mismatch — " + "; ".join(reasons),
                    "missing_source": "NONE",
                    "amount_difference": taxable_diff,
                    "raw_invoice": row,
                    "raw_gstr2b": g2b_row,
                })
                continue

            # Fully matched
            matched.append({
                "invoice_number": inv_num,
                "gstin": inv_gstin,
                "vendor_name": inv_vendor,
                "taxable_amount": inv_taxable,
                "igst": inv_igst,
                "cgst": inv_cgst,
                "sgst": inv_sgst,
                "match_status": "MATCHED",
                "raw_invoice": row,
                "raw_gstr2b": g2b_row,
            })

        # GSTR2B rows not consumed → ONLY_IN_GSTR2B
        for key, g2b_row in g2b_lookup.items():
            if key not in consumed_g2b_keys:
                g2b_inv_num = _val(g2b_row, g2b_map.invoice_number)
                unmatched.append({
                    "invoice_number": g2b_inv_num,
                    "gstin": _val(g2b_row, g2b_map.gstin),
                    "mismatch_reason": "Invoice found in GSTR2B but not in uploaded invoices",
                    "missing_source": "INVOICE",
                    "amount_difference": 0.0,
                    "raw_invoice": None,
                    "raw_gstr2b": g2b_row,
                })

        logger.info("[GSTMatchingAgent] matched=%d unmatched=%d", len(matched), len(unmatched))
        return AgentResult(success=True, data={"matched_records": matched, "unmatched_records": unmatched})
