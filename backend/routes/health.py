"""Health check routes."""

import socket

def setup_health_routes(app):
    """Register health routes."""
    
    @app.get("/api/health/gateway")
    def gateway_health():
        """Check if OpenClaw gateway is reachable."""
        try:
            with socket.create_connection(("localhost", 18789), timeout=0.5):
                return {"status": "up"}
        except Exception:
            return {"status": "down"}
