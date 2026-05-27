import io
from pathlib import Path

import pandas as pd
from fastapi.testclient import TestClient

from app.main import app
from app.utils.gstin_validator import validate_gstin

client = TestClient(app)

FIXTURES = Path(__file__).parent / "fixtures"


def _auth_headers() -> dict:
    resp = client.post("/api/v1/auth/login", json={"username": "admin", "password": "Admin@123"})
    return {"Authorization": f"Bearer {resp.json()['access_token']}"}


def _excel_bytes(data: dict) -> bytes:
    buf = io.BytesIO()
    pd.DataFrame(data).to_excel(buf, index=False)
    return buf.getvalue()


# ── GSTIN validator ────────────────────────────────────────────────────────────

def test_gstin_valid():
    assert validate_gstin("27AABCU9603R1ZX") is True
    assert validate_gstin("07AAGCM4186P1ZX") is True


def test_gstin_invalid():
    assert validate_gstin("") is False
    assert validate_gstin("INVALID") is False
    assert validate_gstin("27AABCU9603R1Z") is False   # too short (14 chars)
    assert validate_gstin("27AABCU9603R1ZXY") is False  # too long (16 chars)


def test_gstin_case_normalised():
    # validator normalises to uppercase — lowercase input is accepted
    assert validate_gstin("27aabcu9603r1zx") is True


# ── Invoice upload ─────────────────────────────────────────────────────────────

def test_upload_invoice_valid():
    headers = _auth_headers()
    with open(FIXTURES / "sample_invoice.xlsx", "rb") as f:
        resp = client.post("/api/v1/upload/invoices", files={"file": ("sample_invoice.xlsx", f, "application/octet-stream")}, headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["row_count"] == 5
    assert "invoice_number" in data["columns"]
    assert "temp_key" in data
    assert len(data["preview"]) <= 3


def test_upload_gstr2b_valid():
    headers = _auth_headers()
    with open(FIXTURES / "sample_gstr2b.xlsx", "rb") as f:
        resp = client.post("/api/v1/upload/gstr2b", files={"file": ("sample_gstr2b.xlsx", f, "application/octet-stream")}, headers=headers)
    assert resp.status_code == 200
    assert resp.json()["row_count"] == 5


def test_upload_wrong_file_type():
    headers = _auth_headers()
    resp = client.post(
        "/api/v1/upload/invoices",
        files={"file": ("data.txt", b"hello", "text/plain")},
        headers=headers,
    )
    assert resp.status_code == 400


def test_upload_any_columns_accepted():
    """Any column names are accepted — no strict schema required."""
    headers = _auth_headers()
    any_col_bytes = _excel_bytes({"col_a": [1, 2], "col_b": [3, 4]})
    resp = client.post(
        "/api/v1/upload/invoices",
        files={"file": ("custom.xlsx", any_col_bytes, "application/octet-stream")},
        headers=headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["row_count"] == 2
    assert "col_a" in data["columns"]
    # Warning is generated since no recognised invoice/GSTIN column found
    assert len(data["warnings"]) > 0


def test_upload_requires_auth():
    """Protected endpoint returns 403 without a token."""
    with open(FIXTURES / "sample_invoice.xlsx", "rb") as f:
        resp = client.post("/api/v1/upload/invoices", files={"file": ("sample_invoice.xlsx", f, "application/octet-stream")})
    assert resp.status_code == 403


# ── Start reconciliation session ───────────────────────────────────────────────

def _upload_both(headers: dict) -> tuple[str, str]:
    with open(FIXTURES / "sample_invoice.xlsx", "rb") as f:
        inv_resp = client.post("/api/v1/upload/invoices", files={"file": ("sample_invoice.xlsx", f, "application/octet-stream")}, headers=headers)
    with open(FIXTURES / "sample_gstr2b.xlsx", "rb") as f:
        g2b_resp = client.post("/api/v1/upload/gstr2b", files={"file": ("sample_gstr2b.xlsx", f, "application/octet-stream")}, headers=headers)
    return inv_resp.json()["temp_key"], g2b_resp.json()["temp_key"]


def test_start_reconciliation():
    headers = _auth_headers()
    inv_key, g2b_key = _upload_both(headers)
    resp = client.post(
        "/api/v1/upload/start",
        json={"invoice_temp_key": inv_key, "gstr2b_temp_key": g2b_key, "session_name": "Test Session"},
        headers=headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "session_id" in data
    assert data["status"] == "uploaded"
    assert data["invoice_row_count"] == 5
    assert data["gstr2b_row_count"] == 5


def test_start_reconciliation_invalid_keys():
    headers = _auth_headers()
    resp = client.post(
        "/api/v1/upload/start",
        json={"invoice_temp_key": "bad-key", "gstr2b_temp_key": "also-bad"},
        headers=headers,
    )
    assert resp.status_code == 400
