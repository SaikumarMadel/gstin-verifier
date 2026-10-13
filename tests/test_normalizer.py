"""
Unit tests for GST JSON normalizer.
"""

from app.normalizer import normalize_gst_response, parse_address_components


def test_normalize_gst_response():
    raw_payload = {
        "ntcrbs": "TRD:TRR",
        "adhrVFlag": "Yes",
        "lgnm": "RELIANCE RETAIL LIMITED",
        "stj": "State - Maharashtra,Zone - MUMBAI_SOUTH_WEST,Division - GOREGAON",
        "dty": "Regular",
        "cxdt": "",
        "gstin": "27AABCR1718E1ZP",
        "nba": [
            "Office / Sale Office",
            "Warehouse / Depot",
            "Retail Business"
        ],
        "ekycVFlag": "Not Applicable",
        "cmpRt": "NA",
        "rgdt": "01/07/2017",
        "ctb": "Public Limited Company",
        "pradr": {
            "adr": "Reliance Corporate Park, TTC Industrial Area, Ghansoli, Navi Mumbai, Thane, Maharashtra, 400701"
        },
        "sts": "Active",
        "tradeNam": "RELIANCE RETAIL LIMITED",
        "isFieldVisitConducted": "No",
        "adhrVdt": "18/09/2026",
        "ctj": "State - CBIC,Zone - MUMBAI",
        "einvoiceStatus": "Yes"
    }

    normalized = normalize_gst_response(raw_payload)

    assert normalized["gstin"] == "27AABCR1718E1ZP"
    assert normalized["pan"] == "AABCR1718E"
    assert normalized["legalName"] == "RELIANCE RETAIL LIMITED"
    assert normalized["tradeName"] == "RELIANCE RETAIL LIMITED"
    assert normalized["status"] == "Active"
    assert normalized["isActive"] is True
    assert normalized["constitutionOfBusiness"] == "Public Limited Company"
    assert normalized["taxpayerType"] == "Regular"
    assert normalized["registrationDate"] == "01/07/2017"
    assert normalized["cancellationDate"] is None
    assert normalized["primaryVertical"] == "Office / Sale Office"
    assert normalized["state"]["code"] == "27"
    assert normalized["state"]["name"] == "Maharashtra"
    assert normalized["compliance"]["einvoiceEnabled"] is True
    assert normalized["compliance"]["aadhaarAuthenticated"] is True
    assert normalized["address"]["pincode"] == "400701"
    assert normalized["address"]["state"] == "Maharashtra"


def test_parse_address_components():
    addr = "Plot 42, MIDC Industrial Area, Pune, Maharashtra, 411018"
    parsed = parse_address_components(addr, "27")
    assert parsed["pincode"] == "411018"
    assert parsed["state"] == "Maharashtra"
    assert parsed["city"] == "Pune"
