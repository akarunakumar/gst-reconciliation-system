import re

_GSTIN_PATTERN = re.compile(r"^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$")


def validate_gstin(gstin: str) -> bool:
    if not gstin:
        return False
    return bool(_GSTIN_PATTERN.match(gstin.strip().upper()))
