"""
Unit tests for GSTIN Validator and Modulo-36 Checksum.
"""

import pytest
from app.validator import validate_gstin, compute_gstin_checksum


def test_valid_gstin_maharashtra():
    # Reliance Retail Limited - Maharashtra
    gstin = "27AABCR1718E1ZP"
    res = validate_gstin(gstin)
    assert res["valid"] is True
    assert res["pan"] == "AABCR1718E"
    assert res["stateCode"] == "27"
    assert res["stateName"] == "Maharashtra"
    assert res["entityNumber"] == "1"
    assert res["checksum"]["valid"] is True
    assert res["checksum"]["expected"] == "P"
    assert len(res["errors"]) == 0


def test_valid_gstin_haryana():
    # Reliance Retail Limited - Haryana
    gstin = "06AABCR1718E1ZT"
    res = validate_gstin(gstin)
    assert res["valid"] is True
    assert res["pan"] == "AABCR1718E"
    assert res["stateCode"] == "06"
    assert res["stateName"] == "Haryana"
    assert res["checksum"]["valid"] is True


def test_invalid_checksum():
    # Last digit altered from P to Q
    gstin = "27AABCR1718E1ZQ"
    res = validate_gstin(gstin)
    assert res["valid"] is False
    assert res["checksum"]["valid"] is False
    assert any("Checksum mismatch" in err for err in res["errors"])


def test_invalid_length():
    res = validate_gstin("27AABCR1718E1Z")  # 14 chars
    assert res["valid"] is False
    assert any("exactly 15 characters" in err for err in res["errors"])


def test_invalid_state_code():
    # State code 98 does not exist in India
    res = validate_gstin("98AABCR1718E1Z1")
    assert res["valid"] is False
    assert any("Invalid state code" in err for err in res["errors"])


def test_invalid_pan_structure():
    # Digits where letters should be in PAN
    res = validate_gstin("27123451718E1ZP")
    assert res["valid"] is False
    assert any("PAN" in err for err in res["errors"])


def test_modulo36_checksum_computation():
    assert compute_gstin_checksum("27AABCR1718E1Z") == "P"
    assert compute_gstin_checksum("06AABCR1718E1Z") == "T"
