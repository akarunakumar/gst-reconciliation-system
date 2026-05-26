from dataclasses import dataclass

_INVOICE_NUM = {"invoice_number","invoice_no","invoice_no.","inv_no","inv_number","bill_no","bill_number","doc_no","voucher_no","document_number","ref_no","particulars","invoice","inv"}
_GSTIN       = {"gstin","gstin_of_supplier","supplier_gstin","party_gstin","gst_no","gstin_no","gstin_no.","gstno","gstin_supplier"}
_TAXABLE     = {"taxable_amount","taxable_value","taxable_amt","base_amount","assessable_value","taxable_value_rs","taxable","taxableamount"}
_IGST        = {"igst","igst_amount","integrated_tax","igst_rs","integrated_tax__","igst_amount_rs"}
_CGST        = {"cgst","cgst_amount","central_tax","cgst_rs","central_tax__"}
_SGST        = {"sgst","sgst_amount","state_tax","sgst_ut_tax","sgst_rs","state_ut_tax","state_ut_tax__"}
_VENDOR      = {"vendor_name","supplier_name","party_name","trade_legal_name","tradelegalnameofthesupplier","supplier","name","party","vendorname"}


@dataclass
class ColumnMap:
    invoice_number: str | None = None
    gstin: str | None = None
    taxable_amount: str | None = None
    igst: str | None = None
    cgst: str | None = None
    sgst: str | None = None
    vendor_name: str | None = None


def _match(keys: list[str], aliases: set[str]) -> str | None:
    for k in keys:
        if k.lower() in aliases:
            return k
    return None


def detect_columns(rows: list[dict]) -> ColumnMap:
    if not rows:
        return ColumnMap()
    keys = list(rows[0].keys())
    return ColumnMap(
        invoice_number=_match(keys, _INVOICE_NUM),
        gstin=_match(keys, _GSTIN),
        taxable_amount=_match(keys, _TAXABLE),
        igst=_match(keys, _IGST),
        cgst=_match(keys, _CGST),
        sgst=_match(keys, _SGST),
        vendor_name=_match(keys, _VENDOR),
    )
