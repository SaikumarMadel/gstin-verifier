"""
GST Portal HTTP Client.
Manages communication with the official Indian GST portal (services.gst.gov.in).
"""

import base64
import time
import requests
from typing import Tuple, Dict, Any
from .config import Config
from .constants import PORTAL_ERROR_CODES

GST_SEARCH_URL = "https://services.gst.gov.in/services/searchtp"
GST_CAPTCHA_URL = "https://services.gst.gov.in/services/captcha"
GST_DETAILS_URL = "https://services.gst.gov.in/services/api/search/taxpayerDetails"

DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://services.gst.gov.in/services/searchtp",
    "Origin": "https://services.gst.gov.in",
    "Sec-Ch-Ua": '"Not-A.Brand";v="99", "Chromium";v="124"',
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": '"Windows"',
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
}


class GSTPortalError(Exception):
    def __init__(self, error_code: str, message: str, status_code: int = 400, raw: Any = None):
        super().__init__(message)
        self.error_code = error_code
        self.message = message
        self.status_code = status_code
        self.raw = raw


def create_portal_session() -> requests.Session:
    """Creates a new requests.Session configured with browser headers."""
    session = requests.Session()
    session.headers.update(DEFAULT_HEADERS)
    return session


def fetch_captcha_image() -> Tuple[requests.Session, str]:
    """
    Initializes a session with the GST portal, retrieves a new captcha image,
    and returns (session, base64_image_data_uri).
    """
    session = create_portal_session()
    timeout = Config.GST_PORTAL_TIMEOUT_SECONDS

    try:
        # Step 1: Visit searchtp to establish session and receive essential cookies
        session.get(GST_SEARCH_URL, timeout=timeout)

        # Step 2: Fetch the captcha image associated with this session
        captcha_resp = session.get(GST_CAPTCHA_URL, timeout=timeout)
        if captcha_resp.status_code != 200 or not captcha_resp.content:
            raise GSTPortalError(
                error_code="CAPTCHA_FETCH_FAILED",
                message=f"Failed to fetch captcha from GST portal (HTTP {captcha_resp.status_code})",
                status_code=502
            )

        encoded_image = base64.b64encode(captcha_resp.content).decode("utf-8")
        data_uri = f"data:image/png;base64,{encoded_image}"
        return session, data_uri

    except requests.exceptions.Timeout:
        raise GSTPortalError(
            error_code="PORTAL_TIMEOUT",
            message="GST government portal timed out while fetching captcha.",
            status_code=504
        )
    except requests.exceptions.RequestException as e:
        raise GSTPortalError(
            error_code="PORTAL_CONNECTION_ERROR",
            message=f"Could not connect to GST portal: {str(e)}",
            status_code=502
        )


def query_taxpayer_details(
    session: requests.Session,
    gstin: str,
    captcha: str
) -> Dict[str, Any]:
    """
    Submits the GSTIN and solved captcha to the GST portal using the active session.
    Returns the parsed JSON response or raises a typed GSTPortalError.
    """
    timeout = Config.GST_PORTAL_TIMEOUT_SECONDS
    payload = {
        "gstin": gstin.strip().upper(),
        "captcha": captcha.strip()
    }

    try:
        resp = session.post(GST_DETAILS_URL, json=payload, timeout=timeout)
        
        if resp.status_code != 200:
            raise GSTPortalError(
                error_code="PORTAL_HTTP_ERROR",
                message=f"GST Portal returned HTTP {resp.status_code}",
                status_code=resp.status_code
            )

        data = resp.json()

        # Check for known GST portal error codes
        err_code = data.get("errorCode")
        if err_code:
            known_err = PORTAL_ERROR_CODES.get(err_code)
            if known_err:
                raise GSTPortalError(
                    error_code=known_err["code"],
                    message=known_err["message"],
                    status_code=known_err["status_code"],
                    raw=data
                )
            else:
                raise GSTPortalError(
                    error_code=err_code,
                    message=f"GST portal returned error code {err_code}",
                    status_code=400,
                    raw=data
                )

        # Validate that the response contains taxpayer data (e.g. lgnm or gstin)
        if "lgnm" not in data and "gstin" not in data:
            raise GSTPortalError(
                error_code="INVALID_RESPONSE",
                message="GST portal response did not contain expected taxpayer details.",
                status_code=502,
                raw=data
            )

        return data

    except requests.exceptions.Timeout:
        raise GSTPortalError(
            error_code="PORTAL_TIMEOUT",
            message="GST government portal timed out while verifying details.",
            status_code=504
        )
    except requests.exceptions.RequestException as e:
        raise GSTPortalError(
            error_code="PORTAL_CONNECTION_ERROR",
            message=f"Failed to communicate with GST portal: {str(e)}",
            status_code=502
        )


def check_portal_health() -> Dict[str, Any]:
    """
    Performs a lightweight ping to the GST portal to verify availability and latency.
    """
    start_time = time.time()
    try:
        session = create_portal_session()
        resp = session.get(GST_SEARCH_URL, timeout=Config.GST_PORTAL_TIMEOUT_SECONDS)
        latency_ms = round((time.time() - start_time) * 1000, 2)
        is_healthy = (resp.status_code == 200)

        return {
            "healthy": is_healthy,
            "statusCode": resp.status_code,
            "latencyMs": latency_ms,
            "message": "GST portal is reachable and responsive." if is_healthy else "GST portal returned non-200 status."
        }
    except Exception as e:
        latency_ms = round((time.time() - start_time) * 1000, 2)
        return {
            "healthy": False,
            "statusCode": None,
            "latencyMs": latency_ms,
            "message": f"GST portal unreachable: {str(e)}"
        }
