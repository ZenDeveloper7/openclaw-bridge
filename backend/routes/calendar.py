"""Calendar and cron jobs API — read directly from disk."""

import json
from pathlib import Path
from datetime import datetime

from config import OPENCLAW_DIR


def _load_cron_jobs() -> list[dict]:
    """Read cron jobs from jobs.json."""
    jobs_file = OPENCLAW_DIR / "cron" / "jobs.json"
    if not jobs_file.exists():
        return []
    try:
        data = json.loads(jobs_file.read_text())
        return data.get("jobs", [])
    except Exception:
        return []


def _format_relative_time(ms: int) -> str:
    """Format milliseconds as relative time string."""
    import time
    now_ms = int(time.time() * 1000)
    diff_ms = ms - now_ms
    
    if diff_ms > 0:
        # Future
        mins = diff_ms // 60000
        hours = mins // 60
        days = hours // 24
        if days > 0:
            return f"in {days}d"
        if hours > 0:
            return f"in {hours}h"
        return f"in {mins}m"
    else:
        # Past
        diff_ms = -diff_ms
        mins = diff_ms // 60000
        hours = mins // 60
        days = hours // 24
        if days > 0:
            return f"{days}d ago"
        if hours > 0:
            return f"{hours}h ago"
        return f"{mins}m ago"


def setup_calendar_routes(app):
    """Register calendar routes."""
    
    @app.get("/api/calendar/jobs")
    def list_cron_jobs():
        """List scheduled cron jobs."""
        raw_jobs = _load_cron_jobs()
        
        jobs = []
        for job in raw_jobs:
            if not job.get("enabled", True):
                continue
            
            schedule = job.get("schedule", {})
            state = job.get("state", {})
            
            # Build schedule description
            expr = schedule.get("expr", "")
            tz = schedule.get("tz", "")
            schedule_desc = f"{expr}"
            if tz:
                schedule_desc += f" ({tz})"
            
            # Next/last run
            next_run = _format_relative_time(state.get("nextRunAtMs", 0)) if state.get("nextRunAtMs") else "-"
            last_run = _format_relative_time(state.get("lastRunAtMs", 0)) if state.get("lastRunAtMs") else "-"
            
            jobs.append({
                "id": job.get("id", ""),
                "name": job.get("name", "Unnamed"),
                "schedule": schedule,
                "scheduleDesc": schedule_desc,
                "nextRun": next_run,
                "lastRun": last_run,
                "status": state.get("lastStatus", "idle"),
                "sessionTarget": job.get("sessionTarget", "main"),
                "agent": job.get("agentId", "main")
            })
        
        return jobs
