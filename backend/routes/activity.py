"""Activity log API."""

import httpx
from datetime import datetime
from fastapi import HTTPException

from config import get_gateway_url, get_gateway_token
from models import ActivityEntry


def _parse_gateway_activity(limit: int = 200) -> list[dict]:
    """Fetch activity from gateway."""
    gateway_url = get_gateway_url()
    token = get_gateway_token()
    
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    try:
        with httpx.Client(timeout=10.0) as client:
            resp = client.get(
                f"{gateway_url}/api/sessions",
                headers=headers,
                params={"messageLimit": limit}
            )
            if resp.status_code != 200:
                return []
            
            sessions = resp.json()
            activities = []
            
            for sess in sessions:
                key = sess.get("sessionKey", "")
                agent_id = sess.get("agentId", "unknown")
                msg_count = sess.get("messageCount", 0)
                started = sess.get("startedAt", "")
                
                if started:
                    activities.append({
                        "id": f"session-{key}",
                        "timestamp": started,
                        "type": "session_start",
                        "content": f"Agent {agent_id} started",
                        "source": key
                    })
                
                if msg_count > 0:
                    activities.append({
                        "id": f"messages-{key}",
                        "timestamp": datetime.now().isoformat(),
                        "type": "messages",
                        "content": f"{msg_count} messages exchanged",
                        "source": key
                    })
            
            # Sort by timestamp descending
            activities.sort(key=lambda x: x["timestamp"], reverse=True)
            return activities[:limit]
            
    except Exception:
        return []


def setup_activity_routes(app):
    """Register activity routes."""
    
    @app.get("/api/activity")
    def get_activity(limit: int = 50):
        """Get recent activity."""
        return _parse_gateway_activity(limit)
    
    @app.post("/api/activity")
    def log_activity(entry: ActivityEntry):
        """Log custom activity entry."""
        # For now, just echo back - could be stored locally
        return entry.model_dump()
