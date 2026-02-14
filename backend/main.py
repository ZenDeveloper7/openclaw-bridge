"""OpenClaw Admin Dashboard — Backend API (v2: Control Board)

Modular structure:
- config.py     : Paths, constants, helpers
- models.py     : Pydantic models
- routes/       : API route modules
    - files.py    : File operations
    - kanban.py   : Kanban board
    - agents.py   : Agent info
    - network.py  : Network monitor
    - terminal.py : Terminal execution
    - calendar.py : Cron jobs
    - security.py : Health & security
    - activity.py : Activity log
    - config.py   : Dashboard config
"""

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from routes import register_all_routes

app = FastAPI(title="OpenClaw Admin Dashboard", version="0.3.0")

# ── CORS ──────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routes ───────────────────────────────────────────────────────────
register_all_routes(app)

# ── Static Files ─────────────────────────────────────────────────────
frontend_path = Path(__file__).parent.parent / "frontend"
if frontend_path.exists():
    app.mount("/", StaticFiles(html=True, directory=str(frontend_path)), name="frontend")
