"""
GST constants, state mappings, and portal error definitions.
"""

# Indian State / UT codes according to GST rules
GST_STATE_CODES = {
    "01": {"name": "Jammu and Kashmir", "code": "JK"},
    "02": {"name": "Himachal Pradesh", "code": "HP"},
    "03": {"name": "Punjab", "code": "PB"},
    "04": {"name": "Chandigarh", "code": "CH"},
    "05": {"name": "Uttarakhand", "code": "UK"},
    "06": {"name": "Haryana", "code": "HR"},
    "07": {"name": "Delhi", "code": "DL"},
    "08": {"name": "Rajasthan", "code": "RJ"},
    "09": {"name": "Uttar Pradesh", "code": "UP"},
    "10": {"name": "Bihar", "code": "BR"},
    "11": {"name": "Sikkim", "code": "SK"},
    "12": {"name": "Arunachal Pradesh", "code": "AR"},
    "13": {"name": "Nagaland", "code": "NL"},
    "14": {"name": "Manipur", "code": "MN"},
    "15": {"name": "Mizoram", "code": "MZ"},
    "16": {"name": "Tripura", "code": "TR"},
    "17": {"name": "Meghalaya", "code": "ML"},
    "18": {"name": "Assam", "code": "AS"},
    "19": {"name": "West Bengal", "code": "WB"},
    "20": {"name": "Jharkhand", "code": "JH"},
    "21": {"name": "Odisha", "code": "OR"},
    "22": {"name": "Chhattisgarh", "code": "CT"},
    "23": {"name": "Madhya Pradesh", "code": "MP"},
    "24": {"name": "Gujarat", "code": "GJ"},
    "26": {"name": "Dadra and Nagar Haveli and Daman and Diu", "code": "DN"},
    "27": {"name": "Maharashtra", "code": "MH"},
    "29": {"name": "Karnataka", "code": "KA"},
    "30": {"name": "Goa", "code": "GA"},
    "31": {"name": "Lakshadweep", "code": "LD"},
    "32": {"name": "Kerala", "code": "KL"},
    "33": {"name": "Tamil Nadu", "code": "TN"},
    "34": {"name": "Puducherry", "code": "PY"},
    "35": {"name": "Andaman and Nicobar Islands", "code": "AN"},
    "36": {"name": "Telangana", "code": "TG"},
    "37": {"name": "Andhra Pradesh", "code": "AP"},
    "38": {"name": "Ladakh", "code": "LA"},
    "97": {"name": "Other Territory", "code": "OT"},
    "99": {"name": "Center Jurisdiction", "code": "CJ"},
}

# Known error codes returned by the GST Portal
PORTAL_ERROR_CODES = {
    "SWEB_9034": {
        "code": "INVALID_CAPTCHA",
        "message": "The captcha entered was incorrect or has expired. Please refresh the captcha and try again.",
        "status_code": 400
    },
    "SWEB_9035": {
        "code": "INVALID_GSTIN",
        "message": "The specified GSTIN was not found on the GST portal or is invalid.",
        "status_code": 404
    },
    "SWEB_9032": {
        "code": "INVALID_GSTIN",
        "message": "The specified GSTIN is invalid or not registered in the system.",
        "status_code": 404
    },
    "SWEB_9000": {
        "code": "PORTAL_RATE_LIMIT",
        "message": "The GST portal is experiencing heavy traffic or temporary rate limits.",
        "status_code": 429
    },
    "SWEB_8000": {
        "code": "PORTAL_INTERNAL_ERROR",
        "message": "Internal error occurred on the GST government server.",
        "status_code": 502
    }
}

# Modulo 36 Character lookup table for GSTIN Checksum calculation
GST_CHARS = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
