"""Health-check endpoint.

A tiny liveness probe registered as its own router. It returns 200 with
``{"status": "ok", "timestamp": ...}`` whenever the service is up, and is used
by the Docker ``HEALTHCHECK`` and by callers checking the API is reachable.
"""

from datetime import datetime, timezone

from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/health")
def health() -> dict:
    """Report that the service is up.

    Returns:
        dict: HTTP 200 with ``status`` fixed to ``"ok"`` and ``timestamp`` set
            to the current UTC time in ISO-8601 format.
    """
    return {
        "status": "ok",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
