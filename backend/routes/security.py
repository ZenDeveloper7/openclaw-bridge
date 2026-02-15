"""Security and health API."""

import os
import re
import time
import subprocess
import shutil
import psutil
from pathlib import Path
from datetime import datetime, timezone, timedelta
from fastapi import HTTPException
import httpx

from config import get_gateway_url, get_gateway_token, OPENCLAW_DIR, OPENCLAW_CONFIG, parse_json5


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


def setup_security_routes(app):
    """Register security and health routes."""
    
    @app.get("/api/security")
    def get_security_info():
        """Get security info in the format expected by the frontend."""
        # Get basic info we have
        ssh_secure = False
        ssh_dir = Path.home() / ".ssh"
        if ssh_dir.exists():
            ssh_key = ssh_dir / "id_ed25519"
            ssh_secure = ssh_key.exists() and ssh_key.stat().st_mode & 0o77 == 0

        firewall_enabled = False
        try:
            result = subprocess.run(
                ["sudo", "ufw", "status"],
                capture_output=True, text=True, timeout=5
            )
            firewall_enabled = "Status: active" in result.stdout
        except Exception:
            pass

        # Format as expected by frontend
        threats = {
            "level": "low",
            "failedSSH": 0,
            "blockedMessages": 0
        }

        tailscale = {
            "status": "off"
        }

        ssh = {
            "recent": []
        }

        authEvents = []

        return {
            "threats": threats,
            "tailscale": tailscale,
            "ssh": ssh,
            "authEvents": authEvents,
            # Also include raw data for future use
            "sshHardened": ssh_secure,
            "firewallEnabled": firewall_enabled
        }
    
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
    
    @app.get("/api/stats")
    def get_stats():
        """Get dashboard stats."""
        # Agent count from session files
        agent_count = 0
        try:
            import json
            agents_dir = OPENCLAW_DIR / "agents"
            if agents_dir.exists():
                for agent_dir in agents_dir.iterdir():
                    sf = agent_dir / "sessions" / "sessions.json"
                    if sf.exists():
                        data = json.loads(sf.read_text())
                        agent_count += len(data)
        except Exception:
            pass
        
        # Kanban stats
        kanban_file = OPENCLAW_DIR / "kanban.json"
        kanban_stats = {"total": 0, "backlog": 0, "in-progress": 0, "review": 0, "done": 0}
        if kanban_file.exists():
            try:
                import json
                data = json.loads(kanban_file.read_text())
                tasks = data.get("tasks", [])
                kanban_stats["total"] = len(tasks)
                for t in tasks:
                    status = t.get("status", "backlog")
                    if status in kanban_stats:
                        kanban_stats[status] += 1
            except Exception:
                pass
        
        # Version - read from openclaw.json
        try:
            cfg = parse_json5(OPENCLAW_CONFIG.read_text())
            version = cfg.get("meta", {}).get("lastTouchedVersion", "unknown")
        except Exception:
            version = "unknown"
        
        # Gateway check
        gateway_url = get_gateway_url()
        gateway_running = False
        try:
            with httpx.Client(timeout=2.0) as client:
                resp = client.get(gateway_url)
                gateway_running = resp.status_code == 200
        except Exception:
            pass
        
        # Agent config count
        try:
            import json as _j
            cfg = _j.loads((OPENCLAW_DIR / "openclaw.json").read_text())
            agent_config_count = len(cfg.get("agents", {}).get("list", []))
        except Exception:
            agent_config_count = agent_count
        
        # Workspace size - calculate fresh
        ws_size = 0
        if OPENCLAW_DIR.exists():
            for entry in OPENCLAW_DIR.rglob("*"):
                if entry.is_file():
                    try:
                        ws_size += entry.stat().st_size
                    except Exception:
                        pass
        
        return {
            "version": version,
            "gatewayRunning": gateway_running,
            "agentCount": agent_config_count,
            "agents": agent_count,
            "tasks": kanban_stats,
            "workspaceSize": ws_size,
            "workspaceSizeMB": round(ws_size / (1024 * 1024), 1)
        }
