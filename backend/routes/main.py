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

import os
from pathlib import Path

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import secrets

from routes import register_all_routes

app = FastAPI(title="OpenClaw Admin Dashboard", version="0.3.0")

# ── CORS ──────────────────────────────────────────────────────────────
# Fixed: Environment-based origins, removed allow_credentials, restrictive methods/headers
allowed_origins = os.environ.get("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:8787").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Content-Type", "Authorization", "X-CSRF-Token"],
)

# ── CSRF Protection ───────────────────────────────────────────────────
class CSRFMiddleware:
    """CSRF protection middleware for FastAPI."""
    
    def __init__(self, app):
        self.app = app
        self.csrf_secret = os.environ.get("CSRF_SECRET", secrets.token_hex(32))
    
    async def __call__(self, scope, receive, send):
        """ASGI callable for middleware."""
        from starlette.requests import Request
        from starlette.responses import Response
        
        request = Request(scope, receive, send)
        
        # Skip CSRF check for localhost (development mode)
        client = scope.get("client")
        if client and client[0] in ("127.0.0.1", "::1"):
            await self.app(scope, receive, send)
            return
        
        # Skip CSRF check for GET, HEAD, OPTIONS
        if request.method in ("GET", "HEAD", "OPTIONS"):
            await self.app(scope, receive, send)
            return
        
        # Check CSRF token for state-changing requests
        if request.method in ("POST", "PUT", "DELETE", "PATCH"):
            csrf_token = request.headers.get("X-CSRF-Token")
            session_csrf = request.cookies.get("csrf_token")
            
            # Check header token or cookie token
            if not csrf_token and not session_csrf:
                response = Response(content="CSRF token missing", status_code=403)
                await response(scope, receive, send)
                return
            
            if not secrets.compare_digest(csrf_token or "", session_csrf or ""):
                response = Response(content="CSRF token invalid", status_code=403)
                await response(scope, receive, send)
                return
        
        await self.app(scope, receive, send)

app.add_middleware(CSRFMiddleware)

# ── Routes ───────────────────────────────────────────────────────────
register_all_routes(app)

# ── Static Files ─────────────────────────────────────────────────────
frontend_path = Path(__file__).parent.parent / "frontend"
if frontend_path.exists():
    app.mount("/", StaticFiles(html=True, directory=str(frontend_path)), name="frontend")
