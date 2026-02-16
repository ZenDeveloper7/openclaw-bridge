"""Health check routes."""

import os
import time
import socket
import psutil
import httpx
from fastapi import HTTPException
from pathlib import Path
from datetime import datetime, timezone, timedelta
from config import get_gateway_url, OPENCLAW_DIR

def _format_uptime(seconds: float) -> str:
    """Format uptime in human readable form."""
    days = int(seconds // 86400)
    hours = int((seconds % 86400) // 3600)
    mins = int((seconds % 3600) // 60)
    if days > 0:
        return f"{days}d {hours}h {mins}m"
    elif hours > 0:
        return f"{hours}h {mins}m"
    return f"{mins}m"

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
    
    @app.get("/api/health")
    def get_health():
        """Get system health metrics."""
        # Uptime
        boot_time = psutil.boot_time()
        uptime_seconds = time.time() - boot_time
        
        # Memory
        mem = psutil.virtual_memory()
        
        # Disk
        disk = psutil.disk_usage("/")
        
        # Load average
        try:
            load = os.getloadavg()
            load_avg = {"1min": load[0], "5min": load[1], "15min": load[2]}
        except Exception:
            load_avg = {"1min": 0, "5min": 0, "15min": 0}
        
        # Gateway status - just check if the port responds
        gateway_url = get_gateway_url()
        gateway_online = False
        try:
            with httpx.Client(timeout=3.0) as client:
                resp = client.get(gateway_url)
                gateway_online = resp.status_code == 200
        except Exception:
            pass
        
        return {
            "uptime": _format_uptime(uptime_seconds),
            "uptimeSeconds": int(uptime_seconds),
            "memory": {
                "usedGB": round(mem.used / (1024**3), 1),
                "totalGB": round(mem.total / (1024**3), 1),
                "percent": mem.percent
            },
            "disk": {
                "usedGB": round(disk.used / (1024**3), 1),
                "totalGB": round(disk.total / (1024**3), 1),
                "percent": disk.percent
            },
            "loadAvg": load_avg,
            "processCount": len(psutil.pids()),
            "gatewayOnline": gateway_online,
            "gatewayUrl": gateway_url
        }
