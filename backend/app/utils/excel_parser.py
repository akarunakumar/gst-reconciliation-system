import io
import pandas as pd

GSTR2B_B2B_SHEET = "B2B"
_GST_HEADER_MARKER = "gstin of supplier"


def _normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    df.columns = [
        str(c).strip().lower()
        .replace(" ", "_").replace("/", "_")
        .replace("(", "").replace(")", "")
        .replace("%", "pct").replace("₹", "").replace("-", "_")
        .strip("_")  # remove leading/trailing underscores (e.g. "taxable_value_" → "taxable_value")
        for c in df.columns
    ]
    return df


def _to_records(df: pd.DataFrame) -> list[dict]:
    return df.where(pd.notna(df), None).to_dict(orient="records")


def _find_gst_header_row(df: pd.DataFrame) -> int | None:
    """Return the row index of the GST data header (the row containing 'GSTIN of supplier')."""
    for i in range(min(20, len(df))):
        vals = [str(v).strip().lower() for v in df.iloc[i] if pd.notna(v)]
        if _GST_HEADER_MARKER in vals:
            return i
    return None


def _merge_header_rows(df: pd.DataFrame, top_idx: int) -> list[str]:
    """Merge the merged-cell top header row with the sub-header row below it.

    GSTR portal exports use two rows: the top row has merged cells (e.g. 'Invoice Details'
    spanning columns 2-5), and the sub-row has the actual field names ('Invoice number',
    'Invoice type', ...). The sub-row value wins when both are present.
    """
    top = list(df.iloc[top_idx])
    sub = list(df.iloc[top_idx + 1]) if top_idx + 1 < len(df) else [None] * len(top)
    cols = []
    for t, s in zip(top, sub):
        t_str = str(t).strip() if pd.notna(t) and str(t).strip() not in ("", "nan") else None
        s_str = str(s).strip() if pd.notna(s) and str(s).strip() not in ("", "nan") else None
        cols.append(s_str or t_str or "unnamed")
    return cols


def _parse_sheet(file_bytes: bytes, sheet_name) -> list[dict]:
    """Parse a single sheet, detecting and handling the two-row merged-header GSTR format."""
    raw = pd.read_excel(io.BytesIO(file_bytes), sheet_name=sheet_name, dtype=str, header=None)
    if raw.empty:
        raise ValueError("The uploaded Excel file appears to be empty.")

    header_idx = _find_gst_header_row(raw)
    if header_idx is None:
        # Fallback: treat row 0 as the header
        df = pd.read_excel(io.BytesIO(file_bytes), sheet_name=sheet_name, dtype=str)
        return _to_records(_normalize_columns(df))

    # Check whether the row immediately below is a sub-header row (first cell is blank)
    next_row = raw.iloc[header_idx + 1] if header_idx + 1 < len(raw) else None
    has_sub_header = next_row is not None and (pd.isna(next_row.iloc[0]) or str(next_row.iloc[0]).strip() == "")

    if has_sub_header:
        cols = _merge_header_rows(raw, header_idx)
        data_start = header_idx + 2
    else:
        cols = [str(v).strip() if pd.notna(v) else "unnamed" for v in raw.iloc[header_idx]]
        data_start = header_idx + 1

    data_df = raw.iloc[data_start:].copy()
    data_df.columns = cols
    data_df = data_df.dropna(how="all")  # drop completely empty rows (footers/blanks)
    return _to_records(_normalize_columns(data_df))


def parse_excel(file_bytes: bytes) -> list[dict]:
    """Parse any GST-related Excel file into normalised row dicts.

    Handles:
    - GSTR2B workbooks: reads the 'B2B' sheet instead of the default first sheet
    - GSTR portal merged-header exports: merges the two-row header into flat column names
    - Trailing-underscore column names from '₹' removal (e.g. 'taxable_value_' → 'taxable_value')
    """
    sheet_names = get_sheet_names(file_bytes)
    sheet = GSTR2B_B2B_SHEET if GSTR2B_B2B_SHEET in sheet_names else 0
    rows = _parse_sheet(file_bytes, sheet)
    if not rows:
        raise ValueError("The uploaded Excel file appears to be empty.")
    return rows


def get_sheet_names(file_bytes: bytes) -> list[str]:
    xls = pd.ExcelFile(io.BytesIO(file_bytes))
    return xls.sheet_names
