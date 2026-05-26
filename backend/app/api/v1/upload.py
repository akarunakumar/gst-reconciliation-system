from fastapi import APIRouter, HTTPException, UploadFile, status

from app.schemas.upload import SessionResponse, StartReconciliationRequest, UploadResponse
from app.services.upload_service import create_session, handle_upload
from app.utils.excel_parser import get_sheet_names

router = APIRouter(prefix="/upload", tags=["Upload"])


async def _process_upload(file: UploadFile, file_type: str) -> UploadResponse:
    file_bytes = await file.read()
    result = handle_upload(file.filename or "upload", file_bytes, file_type)

    if not result.success:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=result.errors)

    rows: list[dict] = result.data["rows"]
    columns = list(rows[0].keys()) if rows else []
    preview = rows[:3]
    warnings: list[str] = result.data.get("warnings", [])

    try:
        sheets = get_sheet_names(file_bytes)
    except Exception:
        sheets = []

    return UploadResponse(
        filename=file.filename or "upload",
        row_count=result.data["row_count"],
        columns=columns,
        preview=preview,
        temp_key=result.data["temp_key"],
        warnings=warnings,
        sheets=sheets,
    )


@router.post("/invoices", response_model=UploadResponse)
async def upload_invoices(file: UploadFile):
    return await _process_upload(file, "invoice")


@router.post("/gstr2b", response_model=UploadResponse)
async def upload_gstr2b(file: UploadFile):
    return await _process_upload(file, "gstr2b")


@router.post("/start", response_model=SessionResponse)
def start_reconciliation(body: StartReconciliationRequest):
    session = create_session(body.invoice_temp_key, body.gstr2b_temp_key, body.session_name)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid temp keys. Please re-upload both files.",
        )
    return SessionResponse(
        session_id=session.id,
        status=session.status,
        invoice_row_count=len(session.invoice_rows),
        gstr2b_row_count=len(session.gstr2b_rows),
        message=f"Reconciliation session '{session.session_name}' created successfully.",
    )
