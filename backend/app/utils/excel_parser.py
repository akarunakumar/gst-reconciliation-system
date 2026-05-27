import io
import pandas as pd


def _normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    df.columns = [
        str(c).strip().lower()
        .replace(" ", "_").replace("/", "_")
        .replace("(", "").replace(")", "")
        .replace("%", "pct").replace("₹", "").replace("-", "_")
        for c in df.columns
    ]
    return df


def _to_records(df: pd.DataFrame) -> list[dict]:
    return df.where(pd.notna(df), None).to_dict(orient="records")


def _read_first_sheet(file_bytes: bytes) -> pd.DataFrame:
    df = pd.read_excel(io.BytesIO(file_bytes), sheet_name=0, dtype=str)
    if df.empty:
        raise ValueError("The uploaded Excel file appears to be empty.")
    return df


def parse_excel(file_bytes: bytes) -> list[dict]:
    """Parse any GST-related Excel file into normalised row dicts."""
    df = _normalize_columns(_read_first_sheet(file_bytes))
    return _to_records(df)


def get_sheet_names(file_bytes: bytes) -> list[str]:
    xls = pd.ExcelFile(io.BytesIO(file_bytes))
    return xls.sheet_names
