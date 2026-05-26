from pathlib import Path
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)
FIXTURES = Path(__file__).parent / "fixtures"


def _upload_and_start() -> str:
    """Upload both fixtures and return a session_id."""
    with open(FIXTURES / "sample_invoice.xlsx", "rb") as f:
        inv = client.post("/api/v1/upload/invoices", files={"file": ("sample_invoice.xlsx", f, "application/octet-stream")})
    with open(FIXTURES / "sample_gstr2b.xlsx", "rb") as f:
        g2b = client.post("/api/v1/upload/gstr2b", files={"file": ("sample_gstr2b.xlsx", f, "application/octet-stream")})

    start = client.post("/api/v1/upload/start", json={
        "invoice_temp_key": inv.json()["temp_key"],
        "gstr2b_temp_key": g2b.json()["temp_key"],
        "session_name": "Test Recon",
    })
    return start.json()["session_id"]


def test_run_reconciliation():
    sid = _upload_and_start()
    resp = client.post(f"/api/v1/reconciliation/run/{sid}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "completed"
    assert data["total_invoice_records"] == 5
    assert data["total_gstr2b_records"] == 5


def test_matched_count():
    sid = _upload_and_start()
    client.post(f"/api/v1/reconciliation/run/{sid}")
    resp = client.get(f"/api/v1/reconciliation/matched/{sid}")
    assert resp.status_code == 200
    data = resp.json()
    # INV-001 and INV-003 are exact matches; INV-002 has amount mismatch → in unmatched
    assert data["total"] >= 2


def test_amount_mismatch_detected():
    """INV-002: invoice taxable=25000, GSTR2B taxable=26000 → AMOUNT_MISMATCH in unmatched."""
    sid = _upload_and_start()
    client.post(f"/api/v1/reconciliation/run/{sid}")
    resp = client.get(f"/api/v1/reconciliation/unmatched/{sid}")
    assert resp.status_code == 200
    reasons = [r["mismatch_reason"] for r in resp.json()["items"]]
    assert any("Amount mismatch" in r for r in reasons)


def test_only_in_invoice():
    """INV-004, INV-005 not in GSTR2B → ONLY_IN_INVOICE."""
    sid = _upload_and_start()
    client.post(f"/api/v1/reconciliation/run/{sid}")
    resp = client.get(f"/api/v1/reconciliation/unmatched/{sid}?missing_source=GSTR2B")
    assert resp.status_code == 200
    assert resp.json()["total"] >= 2


def test_only_in_gstr2b():
    """INV-006, INV-007 not in invoice → ONLY_IN_GSTR2B."""
    sid = _upload_and_start()
    client.post(f"/api/v1/reconciliation/run/{sid}")
    resp = client.get(f"/api/v1/reconciliation/unmatched/{sid}?missing_source=INVOICE")
    assert resp.status_code == 200
    assert resp.json()["total"] >= 2


def test_summary_percentages():
    sid = _upload_and_start()
    resp = client.post(f"/api/v1/reconciliation/run/{sid}")
    data = resp.json()
    assert 0 <= data["match_percentage"] <= 100
    assert data["matched_count"] + data["amount_mismatch_count"] + data["gstin_mismatch_count"] + data["only_in_invoice_count"] == data["total_invoice_records"]


def test_summary_endpoint():
    sid = _upload_and_start()
    client.post(f"/api/v1/reconciliation/run/{sid}")
    resp = client.get(f"/api/v1/reconciliation/summary/{sid}")
    assert resp.status_code == 200
    assert resp.json()["session_id"] == sid


def test_pagination():
    sid = _upload_and_start()
    client.post(f"/api/v1/reconciliation/run/{sid}")
    resp = client.get(f"/api/v1/reconciliation/matched/{sid}?page=1&page_size=1")
    assert resp.status_code == 200
    assert len(resp.json()["items"]) <= 1


def test_search_filter():
    sid = _upload_and_start()
    client.post(f"/api/v1/reconciliation/run/{sid}")
    resp = client.get(f"/api/v1/reconciliation/matched/{sid}?search=INV-001")
    assert resp.status_code == 200


def test_export_endpoint():
    sid = _upload_and_start()
    client.post(f"/api/v1/reconciliation/run/{sid}")
    resp = client.get(f"/api/v1/reconciliation/export/{sid}")
    assert resp.status_code == 200
    assert resp.headers["content-type"] == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    assert len(resp.content) > 0


def test_run_invalid_session():
    resp = client.post("/api/v1/reconciliation/run/nonexistent-id")
    assert resp.status_code == 404


def test_summary_before_run():
    sid = _upload_and_start()
    resp = client.get(f"/api/v1/reconciliation/summary/{sid}")
    assert resp.status_code == 400
