"""Agents API — read agent data directly from disk."""

import json
import time
from pathlib import Path
from fastapi import HTTPException
from datetime import datetime, timezone

from config import OPENCLAW_DIR, OPENCLAW_CONFIG, parse_json5


AGENT_ROLES = {
    "main": "Executive Assistant",
    "atlas": "Coding Specialist",
    "jupiter": "Finance Analyst",
    "jarvis": "General Agent",
}

def _get_agents_config() -> list[dict]:
    """Read agents list from openclaw.json."""
    try:
        cfg = parse_json5(OPENCLAW_CONFIG.read_text())
        return cfg.get("agents", {}).get("list", [])
    except Exception:
        return []


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
                sess["agentDirName"] = agent_dir.name
                # Calculate age
                updated = sess.get("updatedAt", 0)
                if updated:
                    sess["ageMs"] = now_ms - updated
                sessions.append(sess)
        except Exception:
            continue
    
    return sessions


def format_ist_time(timestamp_ms):
    """Convert timestamp (ms) to IST formatted string."""
    if not timestamp_ms:
        return "Never"
    try:
        from zoneinfo import ZoneInfo
        dt = datetime.fromtimestamp(timestamp_ms / 1000, tz=ZoneInfo('Asia/Calcutta'))
        return dt.strftime("%b %d, %I:%M %p IST")
    except Exception:
        return "Invalid"


def _mask_session_key(key: str) -> str:
    """Mask session key for security (show only first 8 and last 4 chars)."""
    if not key or len(key) < 12:
        return "••••••••"
    return key[:8] + "••••••••" + key[-4:]


def _format_time_ist(timestamp_ms):
    """Format timestamp as time ago in IST."""
    if not timestamp_ms:
        return "Never"
    try:
        from zoneinfo import ZoneInfo
        ist = ZoneInfo('Asia/Calcutta')
        now = datetime.now(ist)
        dt = datetime.fromtimestamp(timestamp_ms / 1000, tz=ist)
        diff = now - dt
        
        days = diff.days
        seconds = diff.seconds
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        
        if days > 0:
            return f"{days}d ago"
        elif hours > 0:
            return f"{hours}h ago"
        elif minutes > 0:
            return f"{minutes}m ago"
        else:
            return "just now"
    except Exception:
        return "Invalid"


def setup_agents_routes(app):
    """Register agent routes."""
    
    @app.get("/api/agents")
    def list_agents():
        """Get agents from config + session files."""
        try:
            agents_config = _get_agents_config()
            agents_by_id = {a.get("id"): a for a in agents_config}
            
            sessions = _get_all_sessions()
            
            # Find active main sessions (not cron/run, updated in last 30 min)
            now_ms = int(time.time() * 1000)
            active_cutoff = now_ms - (30 * 60 * 1000)  # 30 minutes
            
            active_ids = set()
            active_sessions = {}
            for sess in sessions:
                key = sess.get("key", "")
                if ":run:" in key or "cron:" in key:
                    continue
                parts = key.split(":")
                agent_id = parts[1] if len(parts) > 1 else "unknown"
                
                updated = sess.get("updatedAt", 0)
                if updated < active_cutoff:
                    continue
                
                active_ids.add(agent_id)
                if agent_id not in active_sessions or (updated > active_sessions[agent_id].get("updatedAt", 0)):
                    active_sessions[agent_id] = sess
            
            agents = []
            
            # Active agents
            for agent_id, sess in active_sessions.items():
                cfg = agents_by_id.get(agent_id, {})
                key = sess.get("key", "")
                
                # Get model from config
                model = cfg.get("model", "unknown")
                
                agents.append({
                    "id": agent_id,
                    "name": cfg.get("name", agent_id),
                    "status": "active",
                    "model": model,
                    "sessionKey": _mask_session_key(key),
                    "capabilities": [],
                    "startedAt": None,
                    "messageCount": 0,
                    "updatedAt": sess.get("updatedAt"),
                    "ageMs": sess.get("ageMs", 0)
                })
            
            # Inactive agents
            for cfg in agents_config:
                agent_id = cfg.get("id")
                if agent_id and agent_id not in active_ids:
                    agents.append({
                        "id": agent_id,
                        "name": cfg.get("name", agent_id),
                        "status": "inactive",
                        "model": cfg.get("model"),
                        "sessionKey": None,
                        "capabilities": [],
                        "startedAt": None,
                        "messageCount": 0
                    })
            
            return agents
                
        except Exception as e:
            raise HTTPException(500, str(e))
    
    @app.get("/api/sessions")
    def list_sessions():
        """Get all sessions including subagents."""
        try:
            sessions = _get_all_sessions()
            result = []
            
            now_ms = int(time.time() * 1000)
            thinking_threshold = 30 * 1000  # 30 seconds - "thinking" if updated within this time
            
            for sess in sessions:
                key = sess.get("key", "")
                parts = key.split(":")
                agent_id = parts[1] if len(parts) > 1 else "unknown"
                session_id = key
                
                # Get model from agent config
                agents_config = _get_agents_config()
                agent_config = next((a for a in agents_config if a.get("id") == agent_id), {})
                model = agent_config.get("model", "unknown")
                
                # Get token usage from session
                context_tokens = sess.get("contextTokens", 0)
                total_tokens = sess.get("totalTokens", 0)
                
                # Get channel from session metadata
                channel = sess.get("channel", "unknown")
                
                # Get run count if applicable (cron runs)
                run_count = None
                if "cron:" in key or ":run:" in key:
                    run_count = sess.get("runCount", 1)
                
                # Check if "thinking" (updated within last 30 seconds)
                updated_at = sess.get("updatedAt", 0)
                is_thinking = (now_ms - updated_at) < thinking_threshold if updated_at else False
                
                result.append({
                    "id": session_id,
                    "agentId": agent_id,
                    "model": model,
                    "contextTokens": context_tokens,
                    "totalTokens": total_tokens,
                    "channel": channel,
                    "updatedAt": updated_at,
                    "runCount": run_count,
                    "isSubagent": "subagent" in key,
                    "thinking": is_thinking
                })
            
            return result
                
        except Exception as e:
            raise HTTPException(500, str(e))
