from pydantic import BaseModel


class MatchedRecord(BaseModel):
    invoice_number: str
    gstin: str
    vendor_name: str
    taxable_amount: float
    igst: float
    cgst: float
    sgst: float
    match_status: str       # MATCHED | AMOUNT_MISMATCH | GSTIN_MISMATCH
    raw_invoice: dict
    raw_gstr2b: dict | None = None


class UnmatchedRecord(BaseModel):
    invoice_number: str
    gstin: str
    mismatch_reason: str
    missing_source: str     # INVOICE | GSTR2B
    amount_difference: float
    raw_invoice: dict | None = None
    raw_gstr2b: dict | None = None


class ReconciliationSummary(BaseModel):
    session_id: str
    session_name: str
    status: str
    total_invoice_records: int
    total_gstr2b_records: int
    matched_count: int
    amount_mismatch_count: int
    gstin_mismatch_count: int
    only_in_invoice_count: int
    only_in_gstr2b_count: int
    match_percentage: float
    total_taxable_invoice: float
    total_taxable_gstr2b: float
    taxable_difference: float


class PaginatedMatchedResponse(BaseModel):
    items: list[MatchedRecord]
    total: int
    page: int
    page_size: int


class PaginatedUnmatchedResponse(BaseModel):
    items: list[UnmatchedRecord]
    total: int
    page: int
    page_size: int
