"""Network monitor API."""

from datetime import datetime
from fastapi import HTTPException
from fastapi.responses import StreamingResponse
import asyncio
import json

from config import network_log, network_paused, network_id_counter


def setup_network_routes(app):
    """Register network routes."""
    
    @app.get("/api/network/log")
    def get_network_log(limit: int = 50):
        """Get network activity log."""
        return list(network_log)[-limit:]
    
    @app.post("/api/network/clear")
    def clear_network_log():
        """Clear network log."""
        network_log.clear()
        return {"success": True}
    
    @app.post("/api/network/pause")
    def pause_network(pause: bool = True):
        """Pause/resume network monitoring."""
        global network_paused
        network_paused = pause
        return {"paused": pause}
    
    @app.get("/api/network/tail")
    async def stream_network():
        """Stream network events via SSE."""
        async def event_generator():
            last_id = 0
            while True:
                await asyncio.sleep(2)
                # Send new entries since last check
                current_log = list(network_log)
                new_entries = current_log[last_id:]
                for entry in new_entries:
                    yield f"data: {json.dumps(entry)}\n\n"
                last_id = len(current_log)
        
        return StreamingResponse(event_generator(), media_type="text/event-stream")


def log_network_event(event_type: str, data: dict):
    """Add entry to network log."""
    global network_id_counter, network_paused
    if network_paused:
        return
    
    network_id_counter += 1
    network_log.append({
        "id": network_id_counter,
        "timestamp": datetime.now().isoformat(),
        "type": event_type,
        **data
    })
