"""Agents API — fetch agent info from gateway."""

import httpx
from fastapi import HTTPException

from config import get_gateway_url, get_gateway_token


def setup_agents_routes(app):
    """Register agent routes."""
    
    @app.get("/api/agents")
    def list_agents():
        """Get agents from gateway."""
        gateway_url = get_gateway_url()
        token = get_gateway_token()
        
        headers = {}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        
        try:
            with httpx.Client(timeout=10.0) as client:
                # Get sessions
                resp = client.get(f"{gateway_url}/api/sessions", headers=headers)
                if resp.status_code != 200:
                    raise HTTPException(resp.status_code, "Gateway error")
                
                sessions = resp.json()
                
                # Get config for agent list
                config_resp = client.get(f"{gateway_url}/api/config", headers=headers)
                agents_config = config_resp.json().get("agents", {}) if config_resp.status_code == 200 else {}
                
                # Build agent list
                agents = []
                active_keys = set()
                
                for sess in sessions:
                    key = sess.get("sessionKey", "")
                    agent_id = sess.get("agentId", "unknown")
                    active_keys.add(agent_id)
                    
                    agents.append({
                        "id": agent_id,
                        "name": agents_config.get(agent_id, {}).get("name", agent_id),
                        "status": "active",
                        "model": sess.get("model"),
                        "sessionKey": key,
                        "capabilities": sess.get("capabilities", []),
                        "startedAt": sess.get("startedAt"),
                        "messageCount": sess.get("messageCount", 0)
                    })
                
                # Add inactive configured agents
                for agent_id, cfg in agents_config.items():
                    if agent_id not in active_keys:
                        agents.append({
                            "id": agent_id,
                            "name": cfg.get("name", agent_id),
                            "status": "inactive",
                            "model": cfg.get("model"),
                            "sessionKey": None,
                            "capabilities": cfg.get("capabilities", []),
                            "startedAt": None,
                            "messageCount": 0
                        })
                
                return agents
                
        except httpx.ConnectError:
            raise HTTPException(503, "Gateway offline")
        except Exception as e:
            raise HTTPException(500, str(e))
