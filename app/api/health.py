"""Health-check endpoint.

This is the one working endpoint the skeleton ships with. If it returns 200
with {"status": "ok"}, the foundation is sound and Module 2 can build on it.
"""

from datetime import datetime, timezone

from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/health")
def health() -> dict:
    """Report that the service is up.

    Returns a 200 response with a status flag and the current UTC timestamp.
    """
    return {
        "status": "ok",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
