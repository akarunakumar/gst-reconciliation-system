from typing import Literal

from pydantic import BaseModel

MatchStatus = Literal["MATCHED", "AMOUNT_MISMATCH", "GSTIN_MISMATCH"]
MissingSource = Literal["INVOICE", "GSTR2B", "NONE"]
SessionStatus = Literal["uploaded", "processing", "completed", "error"]


class MatchedRecord(BaseModel):
    invoice_number: str
    gstin: str
    vendor_name: str
    taxable_amount: float
    igst: float
    cgst: float
    sgst: float
    match_status: MatchStatus


class UnmatchedRecord(BaseModel):
    invoice_number: str
    gstin: str
    mismatch_reason: str
    missing_source: MissingSource
    amount_difference: float


class ReconciliationSummary(BaseModel):
    session_id: str
    session_name: str
    status: SessionStatus
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
