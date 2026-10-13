"""
Health and Portal Status routes.
"""

from flask import Blueprint, jsonify
from ..session_store import session_store
from ..gst_client import check_portal_health

health_bp = Blueprint("health", __name__)


@health_bp.route("/health", methods=["GET"])
def health():
    """
    Service health check returning uptime status, active session count, and portal ping.
    """
    portal_health = check_portal_health()
    status = "UP" if portal_health["healthy"] else "DEGRADED"

    return jsonify({
        "status": status,
        "service": "GST-Verification-API",
        "activeSessions": session_store.active_count(),
        "gstPortal": portal_health
    }), (200 if status == "UP" else 503)


@health_bp.route("/api/v1/portal-status", methods=["GET"])
def portal_status():
    """
    Quick status endpoint for ZDN MIS to determine whether to enable auto-fill or manual fallback.
    """
    result = check_portal_health()
    return jsonify({
        "portalAvailable": result["healthy"],
        "latencyMs": result["latencyMs"],
        "message": result["message"]
    }), 200
