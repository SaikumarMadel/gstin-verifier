"""
Normalizes raw government GST portal JSON response into a clean, typed DTO for ZDN MIS.
"""

import re
from typing import Dict, Any, List, Optional
from .constants import GST_STATE_CODES

PINCODE_REGEX = re.compile(r"\b([1-9][0-9]{5})\b")


def parse_address_components(address_str: str, state_code: str) -> Dict[str, Optional[str]]:
    """
    Extracts pincode, state, and best-guess city from the single raw address string returned by GST.
    """
    pincode = None
    city = None
    state_name = GST_STATE_CODES.get(state_code, {}).get("name")

    if not address_str:
        return {
            "full": "",
            "pincode": None,
            "city": None,
            "state": state_name
        }

    # Extract 6-digit Indian pincode
    pin_matches = PINCODE_REGEX.findall(address_str)
    if pin_matches:
        pincode = pin_matches[-1]

    # Split address by comma to extract city candidate
    parts = [p.strip() for p in address_str.split(",") if p.strip()]
    if parts:
        # Pincode is usually at the end, State is usually second to last, City is third to last
        non_pin_parts = [p for p in parts if not PINCODE_REGEX.search(p)]
        if non_pin_parts:
            # If the last non-pin part looks like state name, city is the one before it
            last_part = non_pin_parts[-1]
            if state_name and state_name.lower() in last_part.lower():
                city = non_pin_parts[-2] if len(non_pin_parts) >= 2 else last_part
            else:
                city = non_pin_parts[-1]

    return {
        "full": address_str,
        "pincode": pincode,
        "city": city,
        "state": state_name
    }


def normalize_gst_response(raw_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Transforms the cryptic government GST portal JSON into a clean, developer-friendly schema.
    """
    gstin = raw_data.get("gstin", "").strip().upper()
    legal_name = raw_data.get("lgnm", "").strip()
    trade_name = raw_data.get("tradeNam", "").strip() or legal_name
    
    # Extract PAN directly from characters 3-12 of GSTIN
    pan = gstin[2:12] if len(gstin) >= 12 else ""

    state_code = gstin[:2] if len(gstin) >= 2 else ""
    state_meta = GST_STATE_CODES.get(state_code, {})

    # Extract principal place of address
    pradr = raw_data.get("pradr") or {}
    raw_addr = pradr.get("adr", "") if isinstance(pradr, dict) else ""
    parsed_address = parse_address_components(raw_addr, state_code)

    # Nature of Business activities
    raw_nba = raw_data.get("nba") or []
    if isinstance(raw_nba, list):
        nature_of_business = [item.strip() for item in raw_nba if isinstance(item, str)]
    else:
        nature_of_business = [str(raw_nba).strip()]

    primary_vertical = nature_of_business[0] if nature_of_business else None

    # Status & Constitution
    status = raw_data.get("sts", "").strip() or "Unknown"
    constitution = raw_data.get("ctb", "").strip() or "Unknown"
    taxpayer_type = raw_data.get("dty", "").strip() or "Regular"
    registration_date = raw_data.get("rgdt", "").strip() or None
    cancellation_date = raw_data.get("cxdt", "").strip() or None

    einvoice_status = str(raw_data.get("einvoiceStatus", "")).strip().lower()
    einvoice_enabled = (einvoice_status == "yes")

    aadhaar_status = str(raw_data.get("adhrVFlag", "")).strip().lower()
    aadhaar_authenticated = (aadhaar_status == "yes")

    return {
        "gstin": gstin,
        "legalName": legal_name,
        "tradeName": trade_name,
        "pan": pan,
        "status": status,
        "isActive": status.lower() == "active",
        "constitutionOfBusiness": constitution,
        "taxpayerType": taxpayer_type,
        "registrationDate": registration_date,
        "cancellationDate": cancellation_date,
        "address": parsed_address,
        "natureOfBusiness": nature_of_business,
        "primaryVertical": primary_vertical,
        "state": {
            "code": state_code,
            "name": state_meta.get("name"),
            "shortCode": state_meta.get("code")
        },
        "jurisdiction": {
            "state": raw_data.get("stj", "").strip() or None,
            "center": raw_data.get("ctj", "").strip() or None
        },
        "compliance": {
            "einvoiceEnabled": einvoice_enabled,
            "aadhaarAuthenticated": aadhaar_authenticated,
            "fieldVisitConducted": str(raw_data.get("isFieldVisitConducted", "")).strip().lower() == "yes"
        }
    }
