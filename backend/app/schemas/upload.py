from pydantic import BaseModel


class UploadResponse(BaseModel):
    filename: str
    row_count: int
    columns: list[str]
    preview: list[dict]
    temp_key: str
    warnings: list[str] = []
    sheets: list[str] = []


class StartReconciliationRequest(BaseModel):
    invoice_temp_key: str
    gstr2b_temp_key: str
    session_name: str = ""


class SessionResponse(BaseModel):
    session_id: str
    status: str
    invoice_row_count: int
    gstr2b_row_count: int
    message: str
