def parse_amount(row: dict, col: str | None) -> float:
    """Return the numeric value of `col` in `row`, or 0.0 on any failure."""
    if not col:
        return 0.0
    try:
        return float(str(row.get(col) or "0").replace(",", ""))
    except (ValueError, TypeError):
        return 0.0
