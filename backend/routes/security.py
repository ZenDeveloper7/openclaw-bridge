"""Security and health API."""

import os
import re
import subprocess
import shutil
import psutil
from pathlib import Path
from datetime import datetime, timezone, timedelta
from fastapi import HTTPException
import httpx

from config import get_gateway_url, get_gateway_token, OPENCLAW_DIR


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


def _get_version_fast() -> str:
    """Quick version check for openclaw."""
    try:
        result = subprocess.run(
            ["npx", "openclaw", "--version"],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:
        pass
    return "unknown"


def _get_workspace_size() -> int:
    """Calculate workspace directory size."""
    total = 0
    workspace = OPENCLAW_DIR / "workspace-atlas"
    if workspace.exists():
        for entry in workspace.rglob("*"):
            if entry.is_file():
                try:
                    total += entry.stat().st_size
                except Exception:
                    pass
    return total


def setup_security_routes(app):
    """Register security and health routes."""
    
    @app.get("/api/security")
    def get_security_info():
        """Get security hardening status."""
        # Check SSH config
        ssh_dir = Path.home() / ".ssh"
        ssh_secure = False
        if ssh_dir.exists():
            ssh_key = ssh_dir / "id_ed25519"
            ssh_secure = ssh_key.exists() and ssh_key.stat().st_mode & 0o77 == 0
        
        # Check firewall (simplified)
        firewall_enabled = False
        try:
            result = subprocess.run(
                ["sudo", "ufw", "status"],
                capture_output=True, text=True, timeout=5
            )
            firewall_enabled = "Status: active" in result.stdout
        except Exception:
            pass
        
        # Check recent logins
        recent_logins = []
        try:
            result = subprocess.run(
                ["last", "-n", "5", "-t"],
                capture_output=True, text=True, timeout=5
            )
            for line in result.stdout.strip().split("\n"):
                if line and "wtmp" not in line:
                    recent_logins.append(line.strip())
        except Exception:
            pass
        
        return {
            "sshHardened": ssh_secure,
            "firewallEnabled": firewall_enabled,
            "recentLogins": recent_logins,
            "openclawVersion": _get_version_fast(),
            "workspaceSize": _get_workspace_size()
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
        
        # Gateway status
        gateway_url = get_gateway_url()
        gateway_online = False
        try:
            with httpx.Client(timeout=3.0) as client:
                resp = client.get(f"{gateway_url}/api/health")
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
        # Agent count
        gateway_url = get_gateway_url()
        token = get_gateway_token()
        agent_count = 0
        
        headers = {}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        
        try:
            with httpx.Client(timeout=5.0) as client:
                resp = client.get(f"{gateway_url}/api/sessions", headers=headers)
                if resp.status_code == 200:
                    agent_count = len(resp.json())
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
        
        return {
            "agents": agent_count,
            "tasks": kanban_stats,
            "workspaceSize": _get_workspace_size()
        }


import time
