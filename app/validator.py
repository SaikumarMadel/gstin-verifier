"""
GSTIN Validator and Checksum Calculator.
Performs offline format validation, state verification, PAN extraction, and Modulo-36 checksum calculation.
"""

import re
from typing import Dict, Any, List
from .constants import GST_STATE_CODES, GST_CHARS

# Standard 15-character GSTIN regex
GSTIN_REGEX = re.compile(r"^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$")

# Indian PAN regex (Chars 3-12 of GSTIN)
PAN_REGEX = re.compile(r"^[A-Z]{5}[0-9]{4}[A-Z]{1}$")


def compute_gstin_checksum(first_14_chars: str) -> str:
    """
    Computes the 15th character (check digit) of a GSTIN using the Modulo-36 algorithm.
    """
    total = 0
    mod = len(GST_CHARS)  # 36
    for i, ch in enumerate(first_14_chars.upper()):
        if ch not in GST_CHARS:
            return ""
        code_point = GST_CHARS.index(ch)
        factor = 1 if (i % 2 == 0) else 2
        product = code_point * factor
        total += (product // mod) + (product % mod)

    remainder = total % mod
    check_code = (mod - remainder) % mod
    return GST_CHARS[check_code]


def validate_gstin(gstin: str) -> Dict[str, Any]:
    """
    Validates a GSTIN string and extracts its components.
    Returns a structured dictionary with validation status and metadata.
    """
    errors: List[str] = []
    
    if not gstin or not isinstance(gstin, str):
        return {
            "valid": False,
            "gstin": gstin or "",
            "errors": ["GSTIN is required and must be a string."]
        }

    clean_gstin = gstin.strip().upper()

    if len(clean_gstin) != 15:
        errors.append(f"GSTIN must be exactly 15 characters long (provided {len(clean_gstin)}).")

    if not GSTIN_REGEX.match(clean_gstin):
        errors.append("GSTIN does not match standard Indian GST format (e.g. 27AAACZ1234A1Z5).")

    state_code = clean_gstin[:2] if len(clean_gstin) >= 2 else ""
    state_info = GST_STATE_CODES.get(state_code)
    if not state_info:
        errors.append(f"Invalid state code '{state_code}'. Must be between 01 and 38, or 97/99.")

    pan = clean_gstin[2:12] if len(clean_gstin) >= 12 else ""
    if not PAN_REGEX.match(pan):
        errors.append(f"Embedded PAN '{pan}' is invalid.")

    checksum_expected = ""
    checksum_actual = clean_gstin[14] if len(clean_gstin) == 15 else ""
    checksum_valid = False

    if len(clean_gstin) == 15:
        checksum_expected = compute_gstin_checksum(clean_gstin[:14])
        checksum_valid = (checksum_expected == checksum_actual)
        if not checksum_valid:
            errors.append(
                f"Checksum mismatch: expected '{checksum_expected}', but received '{checksum_actual}'."
            )

    is_valid = len(errors) == 0

    return {
        "valid": is_valid,
        "gstin": clean_gstin,
        "pan": pan,
        "stateCode": state_code,
        "stateName": state_info["name"] if state_info else None,
        "stateShortCode": state_info["code"] if state_info else None,
        "entityNumber": clean_gstin[12] if len(clean_gstin) >= 13 else None,
        "checksum": {
            "expected": checksum_expected,
            "actual": checksum_actual,
            "valid": checksum_valid
        },
        "errors": errors
    }
