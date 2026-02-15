"""Dashboard config API."""

import json
from pathlib import Path
from fastapi import HTTPException

from config import DASHBOARD_CONFIG_FILE, OPENCLAW_CONFIG
from models import DashboardConfig, ConfigPatch


def _load_dashboard_config() -> dict:
    """Load dashboard config from file."""
    if DASHBOARD_CONFIG_FILE.exists():
        try:
            return json.loads(DASHBOARD_CONFIG_FILE.read_text())
        except Exception:
            pass
    return DashboardConfig().model_dump()


def _save_dashboard_config(config: dict):
    """Save dashboard config to file."""
    DASHBOARD_CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    DASHBOARD_CONFIG_FILE.write_text(json.dumps(config, indent=2))


def setup_config_routes(app):
    """Register config routes."""
    
    @app.get("/api/dashboard/config")
    def get_config():
        """Get dashboard config."""
        return _load_dashboard_config()
    
    @app.post("/api/dashboard/config")
    def update_config(patch: ConfigPatch):
        """Update dashboard config."""
        config = _load_dashboard_config()
        
        # Apply patch
        if patch.boardName is not None:
            config["boardName"] = patch.boardName
        if patch.icon is not None:
            config["icon"] = patch.icon
        if patch.theme is not None:
            config["theme"] = patch.theme
        if patch.accentColor is not None:
            config["accentColor"] = patch.accentColor
        
        _save_dashboard_config(config)
        return config
    
    @app.get("/api/openclaw/config")
    def get_openclaw_config():
        """Read openclaw.json."""
        if not OPENCLAW_CONFIG.exists():
            raise HTTPException(404, "openclaw.json not found")
        try:
            return json.loads(OPENCLAW_CONFIG.read_text())
        except Exception as e:
            raise HTTPException(500, str(e))
    
    @app.put("/api/openclaw/config")
    def save_openclaw_config(body: dict):
        """Save openclaw.json."""
        try:
            OPENCLAW_CONFIG.write_text(json.dumps(body, indent=2))
            return {"success": True}
        except Exception as e:
            raise HTTPException(500, str(e))
