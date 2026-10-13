"""
Main API endpoints for GST verification, captcha acquisition, and GSTIN validation.
Includes full backwards compatibility with shubham-dube/GST-Verification-API.
"""

from flask import Blueprint, request, jsonify
from ..config import Config
from ..session_store import session_store
from ..validator import validate_gstin
from ..normalizer import normalize_gst_response
from ..gst_client import (
    fetch_captcha_image,
    query_taxpayer_details,
    GSTPortalError
)

api_bp = Blueprint("api", __name__)


def check_auth() -> bool:
    """Verifies optional API key if configured in environment."""
    if not Config.API_KEY:
        return True
    
    auth_header = request.headers.get("Authorization", "")
    api_key_header = request.headers.get("X-API-Key", "")
    
    if api_key_header == Config.API_KEY:
        return True
    if auth_header.startswith("Bearer ") and auth_header[7:].strip() == Config.API_KEY:
        return True
    return False


@api_bp.before_request
def authenticate():
    if not check_auth():
        return jsonify({
            "success": False,
            "error": "UNAUTHORIZED",
            "message": "Invalid or missing API Key in request headers."
        }), 401


# ==============================================================================
# Modern Enterprise Endpoints (V1 Recommended)
# ==============================================================================

@api_bp.route("/api/v1/captcha", methods=["GET"])
def get_captcha():
    """
    Acquires a fresh session and captcha image from the GST portal.
    """
    try:
        session, captcha_data_uri = fetch_captcha_image()
        session_id = session_store.create_session(session)

        return jsonify({
            "success": True,
            "sessionId": session_id,
            "captcha": captcha_data_uri,
            "expiresIn": Config.SESSION_TTL_SECONDS
        }), 200

    except GSTPortalError as e:
        return jsonify({
            "success": False,
            "error": e.error_code,
            "message": e.message
        }), e.status_code
    except Exception as e:
        return jsonify({
            "success": False,
            "error": "SERVER_ERROR",
            "message": f"Unexpected error while fetching captcha: {str(e)}"
        }), 500


@api_bp.route("/api/v1/verify", methods=["POST"])
def verify_gstin():
    """
    Verifies a GSTIN with user-supplied captcha.
    Returns normalized ZDN MIS data structure + raw government payload.
    """
    body = request.get_json(silent=True) or {}
    session_id = body.get("sessionId", "").strip()
    gstin = body.get("gstin", "").strip().upper()
    captcha = body.get("captcha", "").strip()

    if not session_id:
        return jsonify({
            "success": False,
            "error": "MISSING_SESSION_ID",
            "message": "Session ID is required. Please call /api/v1/captcha first."
        }), 400

    if not gstin:
        return jsonify({
            "success": False,
            "error": "MISSING_GSTIN",
            "message": "15-character GSTIN is required."
        }), 400

    if not captcha:
        return jsonify({
            "success": False,
            "error": "MISSING_CAPTCHA",
            "message": "Captcha code is required."
        }), 400

    # Offline local validation check
    validation = validate_gstin(gstin)
    if not validation["valid"]:
        return jsonify({
            "success": False,
            "error": "INVALID_GSTIN_FORMAT",
            "message": "The supplied GSTIN is malformed.",
            "details": validation["errors"]
        }), 400

    # Retrieve active session
    session = session_store.get_session(session_id)
    if not session:
        return jsonify({
            "success": False,
            "error": "SESSION_EXPIRED",
            "message": "Your captcha session has expired or is invalid. Please request a new captcha."
        }), 400

    try:
        raw_data = query_taxpayer_details(session, gstin, captcha)
        normalized = normalize_gst_response(raw_data)

        # Release session
        session_store.delete_session(session_id)

        return jsonify({
            "success": True,
            "data": normalized,
            "raw": raw_data
        }), 200

    except GSTPortalError as e:
        # If captcha was invalid, allow the session to remain or prompt refresh
        if e.error_code == "INVALID_CAPTCHA":
            # Session captcha can typically only be used once on GST portal
            session_store.delete_session(session_id)

        return jsonify({
            "success": False,
            "error": e.error_code,
            "message": e.message,
            "raw": e.raw
        }), e.status_code
    except Exception as e:
        session_store.delete_session(session_id)
        return jsonify({
            "success": False,
            "error": "SERVER_ERROR",
            "message": f"Unexpected error during GST verification: {str(e)}"
        }), 500


@api_bp.route("/api/v1/gstin/<gstin>/validate", methods=["GET"])
def validate_gstin_endpoint(gstin: str):
    """
    Performs offline syntactic & checksum validation of a GSTIN.
    Zero network latency, no captcha needed.
    """
    result = validate_gstin(gstin)
    return jsonify({
        "success": True,
        "validation": result
    }), (200 if result["valid"] else 400)


# ==============================================================================
# Legacy Endpoints (Compatible with shubham-dube/GST-Verification-API)
# ==============================================================================

@api_bp.route("/api/v1/getCaptcha", methods=["GET"])
def legacy_get_captcha():
    """
    Backwards-compatible endpoint for existing consumers of the reference repo.
    """
    try:
        session, captcha_data_uri = fetch_captcha_image()
        session_id = session_store.create_session(session)

        return jsonify({
            "sessionId": session_id,
            "image": captcha_data_uri
        }), 200
    except Exception as e:
        return jsonify({"error": "Error in fetching captcha", "details": str(e)}), 500


@api_bp.route("/api/v1/getGSTDetails", methods=["POST"])
def legacy_get_gst_details():
    """
    Backwards-compatible endpoint for existing consumers of the reference repo.
    """
    body = request.get_json(silent=True) or {}
    session_id = body.get("sessionId")
    gstin = body.get("GSTIN") or body.get("gstin")
    captcha = body.get("captcha")

    session = session_store.get_session(session_id)
    if session is None:
        return jsonify({"error": "Invalid session id"}), 400

    try:
        raw_data = query_taxpayer_details(session, gstin, captcha)
        session_store.delete_session(session_id)
        return jsonify(raw_data), 200
    except GSTPortalError as e:
        return jsonify(e.raw or {"error": e.message}), e.status_code
    except Exception as e:
        return jsonify({"error": "Error in fetching GST Details", "details": str(e)}), 500
