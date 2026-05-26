import logging
from app.orchestration.base_agent import AgentResult
from app.orchestration.matching_agent import GSTMatchingAgent
from app.orchestration.summary_agent import SummaryGenerationAgent
from app.utils.column_detector import detect_columns

logger = logging.getLogger(__name__)


class ReconciliationOrchestrator:
    def __init__(self):
        self._matching_agent = GSTMatchingAgent()
        self._summary_agent = SummaryGenerationAgent()

    def process(self, invoice_rows: list[dict], gstr2b_rows: list[dict]) -> AgentResult:
        invoice_col_map = detect_columns(invoice_rows)
        gstr2b_col_map = detect_columns(gstr2b_rows)

        logger.info("Invoice cols detected: %s", invoice_col_map)
        logger.info("GSTR2B cols detected: %s", gstr2b_col_map)

        context = {
            "invoice_rows": invoice_rows,
            "gstr2b_rows": gstr2b_rows,
            "invoice_col_map": invoice_col_map,
            "gstr2b_col_map": gstr2b_col_map,
        }

        result = self._matching_agent.run(context)
        if not result.success:
            return result
        context.update(result.data)

        result = self._summary_agent.run(context)
        if not result.success:
            return result
        context.update(result.data)

        return AgentResult(success=True, data={
            "matched_records": context["matched_records"],
            "unmatched_records": context["unmatched_records"],
            "summary": context["summary"],
            "invoice_col_map": invoice_col_map,
            "gstr2b_col_map": gstr2b_col_map,
        })
