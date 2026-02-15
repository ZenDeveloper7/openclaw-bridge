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


def _describe_cron(expr: str) -> str:
    """Convert a cron expression to a human-friendly description."""
    parts = expr.strip().split()
    if len(parts) != 5:
        return expr
    
    minute, hour, dom, month, dow = parts
    
    def ordinal(n: int) -> str:
        return "th" if 4 <= n % 100 <= 20 else {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    
    try:
        # Every N minutes: */N * * * *
        if minute.startswith('*/') and hour == '*' and dom == '*' and month == '*' and dow == '*':
            n = int(minute[2:])
            return f"Every {n} minute{'s' if n != 1 else ''}"
        
        # Every N hours: 0 */N * * *
        if minute == '0' and hour.startswith('*/') and dom == '*' and month == '*' and dow == '*':
            n = int(hour[2:])
            return f"Every {n} hour{'s' if n != 1 else ''}"
        
        # Every N days: 0 0 */N * *
        if minute == '0' and hour == '0' and dom.startswith('*/') and month == '*' and dow == '*':
            n = int(dom[2:])
            return f"Every {n} day{'s' if n != 1 else ''}"
        
        # Daily at specific time: N M * * *
        if minute != '*' and hour != '*' and dom == '*' and month == '*' and dow == '*':
            try:
                h = int(hour)
                m = int(minute)
                time_str = f"{h:02d}:{m:02d}"
                return f"Daily at {time_str}"
            except:
                pass
        
        # Daily at midnight: 0 0 * * *
        if minute == '0' and hour == '0' and dom == '*' and month == '*' and dow == '*':
            return "Daily at midnight"
        
        # Weekly on specific day(s): 0 0 * * 1,3,5 (Mon,Wed,Fri)
        if minute == '0' and hour == '0' and dom == '*' and month == '*' and dow != '*':
            days = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
            try:
                dow_nums = [int(x) for x in dow.split(',')]
                day_names = [days[d] for d in dow_nums if 0 <= d <= 6]
                if day_names:
                    return f"Weekly on {', '.join(day_names)}"
            except:
                pass
        
        # Monthly on day 1: 0 0 1 * *
        if dom == '1' and month == '*' and dow == '*':
            return "Monthly on day 1st"
        
        # Monthly on specific days: N1,N2,... * * (any time)
        if dom not in ['*', '?'] and month == '*' and dow == '*':
            try:
                days = [int(d) for d in dom.split(',')]
                if len(days) == 1:
                    return f"Monthly on day {days[0]}{ordinal(days[0])}"
                else:
                    day_strs = [f"{d}{ordinal(d)}" for d in sorted(days)]
                    return "Monthly on days " + ', '.join(day_strs)
            except:
                pass
        
    except Exception:
        pass
    
    return expr


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
            human_desc = _describe_cron(expr)
            tz = schedule.get("tz", "")
            schedule_desc = human_desc
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
                "agent": job.get("agentId", "main"),
                "payload": job.get("payload")
            })
        
        return jobs
