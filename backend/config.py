"""Configuration helpers and constants."""

import os
import re
import json
import shutil
import logging
from pathlib import Path
from collections import deque

logger = logging.getLogger("admin-dashboard")

# ── Paths ───────────────────────────────────────────────────────────────
OPENCLAW_DIR = Path(os.environ.get("OPENCLAW_DIR", Path.home() / ".openclaw"))
OPENCLAW_CONFIG = OPENCLAW_DIR / "openclaw.json"
KANBAN_FILE = Path(__file__).parent.parent / "kanban.json"
DASHBOARD_DATA_DIR = Path(__file__).parent.parent / "data"
DASHBOARD_CONFIG_FILE = DASHBOARD_DATA_DIR / "dashboard-config.json"

# ── State (in-memory) ─────────────────────────────────────────────────
network_log = deque(maxlen=500)
network_paused = False
network_id_counter = 0


# ── Helpers ───────────────────────────────────────────────────────────

def _find_qmd() -> str | None:
    """Find the qmd binary via env var or PATH."""
    env_qmd = os.environ.get("QMD_PATH")
    if env_qmd and Path(env_qmd).exists():
        return env_qmd
    return shutil.which("qmd")


def parse_json5(text: str) -> dict:
    """Parse JSON with trailing commas (JSON5-lite) that OpenClaw may produce."""
    cleaned = re.sub(r',\s*([}\]])', r'\1', text)
    return json.loads(cleaned)


def get_gateway_url() -> str:
    if OPENCLAW_CONFIG.exists():
        try:
            cfg = parse_json5(OPENCLAW_CONFIG.read_text())
            port = cfg.get("gateway", {}).get("port", 18789)
            return f"http://localhost:{port}"
        except Exception:
            pass
    return "http://localhost:18789"


def get_gateway_token() -> str:
    if OPENCLAW_CONFIG.exists():
        try:
            cfg = parse_json5(OPENCLAW_CONFIG.read_text())
            return cfg.get("gateway", {}).get("auth", {}).get("token", "")
        except Exception:
            pass
    return ""


def get_openclaw_dir() -> Path:
    return OPENCLAW_DIR


def get_kanban_file() -> Path:
    return KANBAN_FILE
