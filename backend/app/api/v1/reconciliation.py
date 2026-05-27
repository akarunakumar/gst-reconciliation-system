from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import Response

from app.core.security import get_current_user
from app.schemas.reconciliation import (
    MatchedRecord, PaginatedMatchedResponse, PaginatedUnmatchedResponse,
    ReconciliationSummary, UnmatchedRecord,
)
from app.services.reconciliation_service import get_session, run_reconciliation
from app.utils.export import generate_excel_export

router = APIRouter(prefix="/reconciliation", tags=["Reconciliation"])

_AuthDep = Depends(get_current_user)


def _require_session(session_id: str):
    session = get_session(session_id)
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Session '{session_id}' not found")
    return session


def _require_completed(session_id: str):
    session = _require_session(session_id)
    if session.status != "completed":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Reconciliation has not been run yet. Call POST /run first.")
    return session


@router.post("/run/{session_id}", response_model=ReconciliationSummary)
def run(session_id: str, _: dict = _AuthDep):
    session = run_reconciliation(session_id)
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Session '{session_id}' not found")
    if session.status == "error":
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Reconciliation engine encountered an error")
    return ReconciliationSummary(session_id=session.id, session_name=session.session_name, status=session.status, **session.summary)


@router.get("/summary/{session_id}", response_model=ReconciliationSummary)
def get_summary(session_id: str, _: dict = _AuthDep):
    session = _require_completed(session_id)
    return ReconciliationSummary(session_id=session.id, session_name=session.session_name, status=session.status, **session.summary)


@router.get("/matched/{session_id}", response_model=PaginatedMatchedResponse)
def get_matched(
    session_id: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: str = Query("", description="Filter by invoice number or GSTIN"),
    match_status: str = Query("", description="Filter by match status"),
    _: dict = _AuthDep,
):
    session = _require_completed(session_id)
    items = session.matched_records

    if search:
        s = search.lower()
        items = [r for r in items if s in str(r.get("invoice_number", "")).lower() or s in str(r.get("gstin", "")).lower()]
    if match_status:
        items = [r for r in items if r.get("match_status", "") == match_status]

    total = len(items)
    start = (page - 1) * page_size
    page_items = [MatchedRecord(**r) for r in items[start: start + page_size]]
    return PaginatedMatchedResponse(items=page_items, total=total, page=page, page_size=page_size)


@router.get("/unmatched/{session_id}", response_model=PaginatedUnmatchedResponse)
def get_unmatched(
    session_id: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: str = Query("", description="Filter by invoice number or GSTIN"),
    missing_source: str = Query("", description="INVOICE | GSTR2B | NONE"),
    _: dict = _AuthDep,
):
    session = _require_completed(session_id)
    items = session.unmatched_records

    if search:
        s = search.lower()
        items = [r for r in items if s in str(r.get("invoice_number", "")).lower() or s in str(r.get("gstin", "")).lower()]
    if missing_source:
        items = [r for r in items if r.get("missing_source", "") == missing_source]

    total = len(items)
    start = (page - 1) * page_size
    page_items = [UnmatchedRecord(**r) for r in items[start: start + page_size]]
    return PaginatedUnmatchedResponse(items=page_items, total=total, page=page, page_size=page_size)


@router.get("/export/{session_id}")
def export_excel(session_id: str, _: dict = _AuthDep):
    session = _require_completed(session_id)
    xlsx_bytes = generate_excel_export(session.matched_records, session.unmatched_records, session.summary)
    filename = f"reconciliation_{session_id[:8]}.xlsx"
    return Response(
        content=xlsx_bytes,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
