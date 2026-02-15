"""Activity log API — read directly from disk."""

import json
import time
from pathlib import Path
from datetime import datetime
from fastapi import HTTPException

from config import OPENCLAW_DIR


def _get_all_sessions() -> list[dict]:
    """Read sessions from all agent session files."""
    sessions = []
    agents_dir = OPENCLAW_DIR / "agents"
    if not agents_dir.exists():
        return sessions
    
    now_ms = int(time.time() * 1000)
    
    for agent_dir in agents_dir.iterdir():
        if not agent_dir.is_dir():
            continue
        sessions_file = agent_dir / "sessions" / "sessions.json"
        if not sessions_file.exists():
            continue
        try:
            data = json.loads(sessions_file.read_text())
            for key, sess in data.items():
                sess["key"] = key
                updated = sess.get("updatedAt", 0)
                if updated:
                    sess["ageMs"] = now_ms - updated
                sessions.append(sess)
        except Exception:
            continue
    
    return sessions


def setup_activity_routes(app):
    """Register activity routes."""
    
    @app.get("/api/activity")
    def get_activity(limit: int = 50):
        """Get recent activity from session files."""
        try:
            sessions = _get_all_sessions()
            
            # Filter to last 24 hours
            now_ms = int(time.time() * 1000)
            cutoff = now_ms - (24 * 60 * 60 * 1000)
            
            activities = []
            for sess in sessions:
                updated_at = sess.get("updatedAt", 0)
                if updated_at < cutoff:
                    continue
                
                key = sess.get("key", "")
                parts = key.split(":")
                agent_id = parts[1] if len(parts) > 1 else "unknown"
                
                age_ms = sess.get("ageMs", 0)
                age_mins = age_ms // 60000 if age_ms else 0
                if age_mins < 1:
                    age_str = "just now"
                elif age_mins < 60:
                    age_str = f"{age_mins}m ago"
                elif age_mins < 1440:
                    age_str = f"{age_mins // 60}h {age_mins % 60}m ago"
                else:
                    days = age_mins // 1440
                    hours = (age_mins % 1440) // 60
                    age_str = f"{days}d {hours}h ago"
                
                timestamp = datetime.fromtimestamp(updated_at / 1000).isoformat() if updated_at else datetime.now().isoformat()
                
                # Determine activity type
                activity_type = "session"
                if "cron:" in key:
                    activity_type = "cron"
                elif ":run:" in key:
                    activity_type = "spawn"
                
                activities.append({
                    "id": f"session-{key}",
                    "timestamp": timestamp,
                    "type": activity_type,
                    "content": f"Agent {agent_id} — {age_str}",
                    "source": key,
                    "agent": agent_id,
                    "model": None,
                    "updatedAt": updated_at
                })
            
            activities.sort(key=lambda x: x.get("updatedAt", 0), reverse=True)
            return activities[:limit]
            
        except Exception as e:
            return []
    
    @app.post("/api/activity")
    def log_activity(entry: dict):
        """Log custom activity entry."""
        return entry

    @app.get("/api/activity/log")
    def get_activity_log(limit: int = 200, offset: int = 0, action: str = None):
        """Read the raw activity feed from activity-feed.jsonl."""
        log_file = OPENCLAW_DIR / "activity-feed.jsonl"
        if not log_file.exists():
            return {"total": 0, "offset": 0, "limit": limit, "entries": []}
        
        entries = []
        try:
            with open(log_file, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        entry = json.loads(line)
                        if action and entry.get("action") != action:
                            continue
                        entries.append(entry)
                    except json.JSONDecodeError:
                        continue
        except Exception:
            return {"total": 0, "offset": 0, "limit": limit, "entries": []}
        
        total = len(entries)
        # Newest first
        entries.reverse()
        page = entries[offset: offset + limit]
        return {"total": total, "offset": offset, "limit": limit, "entries": page}
