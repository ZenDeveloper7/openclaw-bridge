"""Calendar and cron jobs API."""

import httpx
from fastapi import HTTPException

from config import get_gateway_url, get_gateway_token


def _parse_cron_schedule_desc(schedule: dict) -> str:
    """Convert cron schedule to human description."""
    kind = schedule.get("kind", "")
    
    if kind == "every":
        every = schedule.get("everyMs", 0)
        if every >= 86400000:
            return f"Every {every // 86400000} day(s)"
        elif every >= 3600000:
            return f"Every {every // 3600000} hour(s)"
        elif every >= 60000:
            return f"Every {every // 60000} minute(s)"
        return f"Every {every}ms"
    
    elif kind == "cron":
        expr = schedule.get("expr", "")
        # Simple cron parsing
        parts = expr.split()
        if len(parts) == 5:
            return f"Cron: {parts[0]} {parts[1]} {parts[2]} {parts[3]} {parts[4]}"
        return f"Cron: {expr}"
    
    elif kind == "at":
        return f"At: {schedule.get('at', '')}"
    
    return "Unknown"


def _get_cron_day_of_week(schedule: dict) -> list[int]:
    """Parse day of week from cron schedule."""
    if schedule.get("kind") != "cron":
        return []
    expr = schedule.get("expr", "").split()
    if len(expr) < 5:
        return []
    
    dow = expr[4]
    if dow == "*":
        return list(range(7))
    
    # Handle ranges like "1-5"
    if "-" in dow:
        start, end = map(int, dow.split("-"))
        return list(range(start, end + 1))
    
    # Handle lists like "1,3,5"
    if "," in dow:
        return [int(d) for d in dow.split(",")]
    
    return [int(dow)]


def setup_calendar_routes(app):
    """Register calendar routes."""
    
    @app.get("/api/calendar/jobs")
    def list_cron_jobs():
        """List scheduled cron jobs from gateway."""
        gateway_url = get_gateway_url()
        token = get_gateway_token()
        
        headers = {}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        
        try:
            with httpx.Client(timeout=10.0) as client:
                resp = client.get(f"{gateway_url}/api/cron/list", headers=headers)
                if resp.status_code != 200:
                    return []
                
                jobs = resp.json()
                
                # Enrich with human-readable schedule
                for job in jobs:
                    job["scheduleDesc"] = _parse_cron_schedule_desc(job.get("schedule", {}))
                    job["daysOfWeek"] = _get_cron_day_of_week(job.get("schedule", {}))
                
                return jobs
                
        except httpx.ConnectError:
            return []
        except Exception:
            return []
