"""Health check routes."""

import socket
from fastapi import APIRouter

router = APIRouter()

@router.get("/health/gateway")
def gateway_health():
    """Check if OpenClaw gateway is reachable."""
    try:
        with socket.create_connection(("localhost", 18789), timeout=0.5):
            return {"status": "up"}
    except Exception:
        return {"status": "down"}
