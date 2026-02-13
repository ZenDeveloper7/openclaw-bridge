"""OpenClaw Admin Dashboard — Backend API (v2: Control Board)"""

import os
import re
import json
import shutil
import subprocess
import time
import asyncio
from pathlib import Path
from datetime import datetime, timezone, timedelta
from collections import deque

import httpx
from fastapi import FastAPI, HTTPException, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

app = FastAPI(title="OpenClaw Admin Dashboard", version="0.2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Configuration (env vars with sensible defaults) ─────────────────
OPENCLAW_DIR = Path(os.environ.get("OPENCLAW_DIR", Path.home() / ".openclaw"))
OPENCLAW_CONFIG = OPENCLAW_DIR / "openclaw.json"
KANBAN_FILE = Path(__file__).parent.parent / "kanban.json"
DASHBOARD_CONFIG_FILE = OPENCLAW_DIR / "dashboard-config.json"


class DashboardConfig(BaseModel):
    boardName: str = "Control Board"
    icon: str = "🦞"
    theme: str = "default"
    accentColor: str = "#f97316"

def _find_qmd() -> str | None:
    """Find the qmd binary via env var or PATH."""
    env_qmd = os.environ.get("QMD_PATH")
    if env_qmd and Path(env_qmd).exists():
        return env_qmd
    return shutil.which("qmd")


def parse_json5(text: str) -> dict:
    """Parse JSON with trailing commas (JSON5-lite) that OpenClaw may produce."""
    # Strip trailing commas before ] or }
    cleaned = re.sub(r',\s*([}\]])', r'\1', text)
    return json.loads(cleaned)

# ── Network Monitor State ───────────────────────────────────────────

network_log: deque = deque(maxlen=500)
network_paused = False
network_id_counter = 0


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


# ── Models ──────────────────────────────────────────────────────────

class FileContent(BaseModel):
    content: str


class FileInfo(BaseModel):
    name: str
    path: str
    is_dir: bool
    size: int | None = None
    modified: str | None = None


class KanbanTask(BaseModel):
    id: str
    title: str
    description: str = ""
    status: str = "backlog"  # backlog | in-progress | review | done
    agent: str = ""  # which agent owns this
    priority: str = "normal"  # low | normal | high | urgent
    tags: list[str] = []
    created: str = ""
    updated: str = ""


class KanbanBoard(BaseModel):
    tasks: list[dict] = []


# ── File Explorer ───────────────────────────────────────────────────

@app.get("/api/files")
async def list_files(path: str = "") -> list[FileInfo]:
    target = OPENCLAW_DIR / path
    target = target.resolve()

    if not str(target).startswith(str(OPENCLAW_DIR.resolve())):
        raise HTTPException(status_code=403, detail="Access denied")

    if not target.exists():
        raise HTTPException(status_code=404, detail="Path not found")

    if not target.is_dir():
        raise HTTPException(status_code=400, detail="Not a directory")

    items = []
    try:
        for entry in sorted(target.iterdir(), key=lambda e: (not e.is_dir(), e.name.lower())):
            if entry.name.startswith(".") and entry.is_dir():
                continue
            stat = entry.stat()
            items.append(FileInfo(
                name=entry.name,
                path=str(entry.relative_to(OPENCLAW_DIR)),
                is_dir=entry.is_dir(),
                size=stat.st_size if not entry.is_dir() else None,
                modified=datetime.fromtimestamp(stat.st_mtime).isoformat(),
            ))
    except PermissionError:
        raise HTTPException(status_code=403, detail="Permission denied")

    return items


@app.get("/api/files/read")
async def read_file(path: str) -> dict:
    target = OPENCLAW_DIR / path
    target = target.resolve()

    if not str(target).startswith(str(OPENCLAW_DIR.resolve())):
        raise HTTPException(status_code=403, detail="Access denied")

    if not target.exists():
        raise HTTPException(status_code=404, detail="File not found")

    if not target.is_file():
        raise HTTPException(status_code=400, detail="Not a file")

    if target.stat().st_size > 5 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="File too large")

    try:
        content = target.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="Binary file, cannot display")

    suffix = target.suffix.lower()
    file_type = "text"
    if suffix == ".json":
        file_type = "json"
    elif suffix == ".jsonl":
        file_type = "jsonl"
    elif suffix in (".md", ".markdown"):
        file_type = "markdown"
    elif suffix in (".py", ".js", ".ts", ".sh", ".yml", ".yaml", ".toml"):
        file_type = "code"

    return {"content": content, "type": file_type, "path": path, "name": target.name}


@app.get("/api/files/image")
async def read_image(path: str):
    """Serve an image file."""
    from fastapi.responses import FileResponse
    target = OPENCLAW_DIR / path
    target = target.resolve()

    if not str(target).startswith(str(OPENCLAW_DIR.resolve())):
        raise HTTPException(status_code=403, detail="Access denied")
    if not target.exists() or not target.is_file():
        raise HTTPException(status_code=404, detail="File not found")

    suffix = target.suffix.lower()
    mime_map = {".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png",
                ".gif": "image/gif", ".webp": "image/webp", ".svg": "image/svg+xml",
                ".bmp": "image/bmp", ".ico": "image/x-icon"}
    media_type = mime_map.get(suffix, "application/octet-stream")

    if target.stat().st_size > 20 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="Image too large (>20MB)")

    return FileResponse(str(target), media_type=media_type)


@app.get("/api/files/jsonl")
async def read_jsonl(path: str, offset: int = 0, limit: int = 100) -> dict:
    target = OPENCLAW_DIR / path
    target = target.resolve()

    if not str(target).startswith(str(OPENCLAW_DIR.resolve())):
        raise HTTPException(status_code=403, detail="Access denied")

    if not target.exists():
        raise HTTPException(status_code=404, detail="File not found")

    lines = []
    total = 0
    try:
        with open(target, "r", encoding="utf-8") as f:
            for i, line in enumerate(f):
                line = line.strip()
                if not line:
                    continue
                total += 1
                if total - 1 < offset:
                    continue
                if len(lines) >= limit:
                    continue
                try:
                    lines.append({"index": total - 1, "data": json.loads(line)})
                except json.JSONDecodeError:
                    lines.append({"index": total - 1, "raw": line, "error": "Invalid JSON"})
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="Binary file")

    return {"lines": lines, "total": total, "offset": offset, "limit": limit, "path": path}


@app.put("/api/files/jsonl/line")
async def update_jsonl_line(path: str, index: int, body: FileContent) -> dict:
    target = OPENCLAW_DIR / path
    target = target.resolve()

    if not str(target).startswith(str(OPENCLAW_DIR.resolve())):
        raise HTTPException(status_code=403, detail="Access denied")

    if not target.exists():
        raise HTTPException(status_code=404, detail="File not found")

    try:
        json.loads(body.content)
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=422, detail=f"Invalid JSON: {e}")

    all_lines = []
    with open(target, "r", encoding="utf-8") as f:
        all_lines = f.readlines()

    real_index = -1
    count = 0
    for i, line in enumerate(all_lines):
        if line.strip():
            if count == index:
                real_index = i
                break
            count += 1

    if real_index == -1:
        raise HTTPException(status_code=404, detail=f"Line {index} not found")

    all_lines[real_index] = body.content.rstrip("\n") + "\n"

    with open(target, "w", encoding="utf-8") as f:
        f.writelines(all_lines)

    return {"ok": True, "path": path, "index": index}


@app.put("/api/files/write")
async def write_file(path: str, body: FileContent) -> dict:
    target = OPENCLAW_DIR / path
    target = target.resolve()

    if not str(target).startswith(str(OPENCLAW_DIR.resolve())):
        raise HTTPException(status_code=403, detail="Access denied")

    if not target.parent.exists():
        raise HTTPException(status_code=404, detail="Parent directory not found")

    if target.suffix.lower() == ".json":
        try:
            json.loads(body.content)
        except json.JSONDecodeError as e:
            raise HTTPException(status_code=422, detail=f"Invalid JSON: {e}")

    target.write_text(body.content, encoding="utf-8")
    await _log_activity("file_write", path, details=f"{len(body.content)} bytes")
    return {"ok": True, "path": path}


# ── File Search ─────────────────────────────────────────────────────

@app.get("/api/files/search")
async def search_files(q: str = "", limit: int = 20) -> list[dict]:
    """Search files by name under ~/.openclaw/"""
    if not q or len(q) < 1:
        return []

    q_lower = q.lower()
    results = []

    try:
        for entry in OPENCLAW_DIR.rglob("*"):
            if entry.is_file() and not any(p.startswith(".") for p in entry.relative_to(OPENCLAW_DIR).parts):
                name = entry.name.lower()
                rel = str(entry.relative_to(OPENCLAW_DIR))
                # Match against filename or full relative path
                if q_lower in name or q_lower in rel.lower():
                    stat = entry.stat()
                    results.append({
                        "name": entry.name,
                        "path": rel,
                        "size": stat.st_size,
                        "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                        "is_dir": False,
                    })
                    if len(results) >= limit:
                        break
    except Exception:
        pass

    # Sort: exact name matches first, then by path length
    results.sort(key=lambda r: (0 if q_lower == r["name"].lower() else 1 if q_lower in r["name"].lower() else 2, len(r["path"])))

    return results


# ── Config ──────────────────────────────────────────────────────────

@app.get("/api/config")
async def get_config() -> dict:
    if not OPENCLAW_CONFIG.exists():
        raise HTTPException(status_code=404, detail="Config not found")

    content = OPENCLAW_CONFIG.read_text()
    try:
        parsed = json.loads(content)
    except json.JSONDecodeError:
        return {"raw": content, "parsed": None}

    return {"raw": content, "parsed": parsed}


# ── Dashboard Config ────────────────────────────────────────────────

def _load_dashboard_config() -> dict:
    """Load dashboard configuration from JSON file."""
    if DASHBOARD_CONFIG_FILE.exists():
        try:
            return json.loads(DASHBOARD_CONFIG_FILE.read_text())
        except (json.JSONDecodeError, PermissionError):
            pass
    return {"boardName": "Control Board", "icon": "🦞", "theme": "default", "accentColor": "#f97316"}


def _save_dashboard_config(config: dict):
    """Save dashboard configuration to JSON file."""
    DASHBOARD_CONFIG_FILE.write_text(json.dumps(config, indent=2))


@app.get("/api/dashboard/config")
async def get_dashboard_config() -> dict:
    """Get dashboard configuration (board name, icon, theme)."""
    return _load_dashboard_config()


@app.post("/api/dashboard/config")
async def update_dashboard_config(config: DashboardConfig) -> dict:
    """Update dashboard configuration."""
    current = _load_dashboard_config()
    updated = {**current, **config.model_dump(exclude_unset=True)}
    _save_dashboard_config(updated)
    return updated


# ── Agent Sessions ──────────────────────────────────────────────────

THINKING_THRESHOLD_MS = 60000

@app.get("/api/agents")
async def list_agents() -> list[dict]:
    if not OPENCLAW_CONFIG.exists():
        return []

    config = parse_json5(OPENCLAW_CONFIG.read_text())
    agents_config = config.get("agents", {})
    agent_list = agents_config.get("list", [])

    current_time = time.time() * 1000

    agents = []
    for agent in agent_list:
        agent_id = agent.get("id", "unknown")
        workspace = agent.get("workspace", agents_config.get("defaults", {}).get("workspace", ""))

        agent_dir = OPENCLAW_DIR / "agents" / agent_id
        sessions_file = agent_dir / "sessions" / "sessions.json"

        session_info = {}
        is_thinking = False
        last_activity = 0

        if sessions_file.exists():
            try:
                session_data = json.loads(sessions_file.read_text())
                session_info = session_data
                updated_at = session_data.get("updatedAt", 0)
                last_activity = max(last_activity, updated_at)
            except (json.JSONDecodeError, PermissionError):
                pass

        if sessions_file.exists():
            try:
                sessions_data = json.loads(sessions_file.read_text())
                for key, session in sessions_data.items():
                    if key.startswith("agent:"):
                        jsonl_path = session.get("sessionFile")
                        if jsonl_path and Path(jsonl_path).exists():
                            mtime_ms = Path(jsonl_path).stat().st_mtime * 1000
                            last_activity = max(last_activity, mtime_ms)
            except Exception:
                pass

        is_thinking = (current_time - last_activity) < THINKING_THRESHOLD_MS

        # Agent role and description mapping
        agent_roles = {
            "main": {"role": "Executive Assistant", "description": "Handles general tasks, messaging, scheduling, and daily operations."},
            "atlas": {"role": "Coding Specialist", "description": "Writes, debugs, and refactors code. Git workflows and technical research."},
            "jupiter": {"role": "Finance Specialist", "description": "Manages finances, budgets, investments, and monetary tasks."},
        }
        
        agent_info = agent_roles.get(agent_id, {"role": "Agent", "description": "Custom agent for specialized tasks."})
        role = agent.get("role") or agent_info["role"]
        description = agent.get("description") or agent_info["description"]

        # Count tasks assigned to this agent from kanban
        task_count = 0
        active_task = None
        if KANBAN_FILE.exists():
            try:
                kanban = json.loads(KANBAN_FILE.read_text())
                for task in kanban.get("tasks", []):
                    if task.get("agent") == agent_id:
                        task_count += 1
                        if task.get("status") == "in-progress" and not active_task:
                            active_task = task.get("title", "")
            except Exception:
                pass

        # Get thinking content from latest session
        thinking_content = ""
        if sessions_file.exists():
            try:
                sessions_data = json.loads(sessions_file.read_text())
                for key, session in sessions_data.items():
                    if key.startswith("agent:"):
                        jsonl_path = session.get("sessionFile")
                        if jsonl_path and Path(jsonl_path).exists():
                            # Read last few lines from jsonl to find thinking
                            with open(jsonl_path, 'r') as f:
                                lines = f.readlines()
                                # Look for thinking in last few lines
                                for line in reversed(lines[-10:]):
                                    try:
                                        entry = json.loads(line)
                                        msg_type = entry.get("type", "")
                                        # Check for thinking_reasoning or message content
                                        if msg_type == "message":
                                            msg = entry.get("message", {})
                                            content = msg.get("content", [])
                                            if isinstance(content, list):
                                                for block in content:
                                                    if block.get("type") == "thinking":
                                                        thinking_content = block.get("thinking", "")[:200]
                                                        break
                                    except:
                                        pass
            except Exception:
                pass

        agents.append({
            "id": agent_id,
            "name": agent.get("name", agent_id),
            "role": role,
            "description": description,
            "model": agent.get("model", agents_config.get("defaults", {}).get("model", {}).get("primary", "unknown")),
            "workspace": Path(workspace).name if workspace else "default",
            "hasAgentDir": agent_dir.exists(),
            "thinking": is_thinking,
            "thinkingContent": thinking_content,
            "lastActivity": last_activity,
            "session": session_info,
            "taskCount": task_count,
            "activeTask": active_task,
        })

    return agents


# ── Kanban Board ────────────────────────────────────────────────────

def _load_kanban() -> dict:
    if KANBAN_FILE.exists():
        try:
            return json.loads(KANBAN_FILE.read_text())
        except (json.JSONDecodeError, PermissionError):
            pass
    return {"tasks": [], "columns": ["backlog", "in-progress", "review", "done"]}


def _save_kanban(data: dict):
    KANBAN_FILE.write_text(json.dumps(data, indent=2))


@app.get("/api/kanban")
async def get_kanban() -> dict:
    return _load_kanban()


@app.post("/api/kanban/task")
async def create_task(task: KanbanTask) -> dict:
    board = _load_kanban()
    now = datetime.now().isoformat()

    new_task = task.model_dump()
    if not new_task["id"]:
        new_task["id"] = f"task-{int(time.time() * 1000)}"
    if not new_task["created"]:
        new_task["created"] = now
    new_task["updated"] = now

    board["tasks"].append(new_task)
    _save_kanban(board)
    await _log_activity("task_create", new_task["title"], agent=new_task.get("agent", ""))
    return new_task


@app.put("/api/kanban/task/{task_id}")
async def update_task(task_id: str, request: Request) -> dict:
    board = _load_kanban()
    body = await request.json()

    for i, task in enumerate(board["tasks"]):
        if task["id"] == task_id:
            task.update(body)
            task["updated"] = datetime.now().isoformat()
            board["tasks"][i] = task
            _save_kanban(board)
            await _log_activity("task_update", task.get("title", task_id), agent=task.get("agent", ""))
            return task

    raise HTTPException(status_code=404, detail="Task not found")


@app.delete("/api/kanban/task/{task_id}")
async def delete_task(task_id: str) -> dict:
    board = _load_kanban()
    deleted_title = ""
    for t in board["tasks"]:
        if t["id"] == task_id:
            deleted_title = t.get("title", task_id)
            break
    board["tasks"] = [t for t in board["tasks"] if t["id"] != task_id]
    _save_kanban(board)
    await _log_activity("task_delete", deleted_title or task_id)
    return {"ok": True}


@app.put("/api/kanban/task/{task_id}/move")
async def move_task(task_id: str, request: Request) -> dict:
    board = _load_kanban()
    body = await request.json()
    new_status = body.get("status", "")

    for i, task in enumerate(board["tasks"]):
        if task["id"] == task_id:
            task["status"] = new_status
            task["updated"] = datetime.now().isoformat()
            board["tasks"][i] = task
            _save_kanban(board)
            await _log_activity("task_move", task.get("title", task_id), agent=task.get("agent", ""), details=f"→ {new_status}")
            return task

    raise HTTPException(status_code=404, detail="Task not found")


# ── Quick Stats ─────────────────────────────────────────────────────

def _get_version_fast() -> str:
    """Get OpenClaw version by searching common node_modules locations."""
    try:
        # Try to find openclaw package.json in common global install paths
        candidates = [
            Path("/opt/homebrew/lib/node_modules/openclaw/package.json"),
            Path("/usr/local/lib/node_modules/openclaw/package.json"),
            Path("/usr/lib/node_modules/openclaw/package.json"),
        ]
        # Also check npm/node global dirs dynamically
        npm_root = shutil.which("npm")
        if npm_root:
            npm_prefix = Path(npm_root).resolve().parent.parent
            candidates.append(npm_prefix / "lib" / "node_modules" / "openclaw" / "package.json")
        # Check mise/asdf/nvm style paths
        home = Path.home()
        for node_dir in (home / ".local" / "share" / "mise" / "installs" / "node").glob("*/lib/node_modules/openclaw/package.json"):
            candidates.append(node_dir)
        for nvm_dir in (home / ".nvm" / "versions" / "node").glob("*/lib/node_modules/openclaw/package.json"):
            candidates.append(nvm_dir)

        for pkg in candidates:
            if pkg.exists():
                data = json.loads(pkg.read_text())
                return data.get("version", "unknown")
    except Exception:
        pass
    return "unknown"


async def _check_gateway_fast() -> bool:
    """Check if gateway is running by probing its WebSocket/HTTP port directly."""
    try:
        async with httpx.AsyncClient(timeout=1.0) as client:
            url = get_gateway_url()
            token = get_gateway_token()
            headers = {"Authorization": f"Bearer {token}"} if token else {}
            resp = await client.get(f"{url}/", headers=headers)
            return resp.status_code < 500
    except Exception:
        return False


# Cache workspace size — recalculate at most once per 60s
_ws_size_cache: dict = {"size": 0, "ts": 0.0}

def _get_workspace_size() -> int:
    now = time.time()
    if now - _ws_size_cache["ts"] < 60:
        return _ws_size_cache["size"]
    total = 0
    try:
        for f in OPENCLAW_DIR.rglob("*"):
            if f.is_file():
                total += f.stat().st_size
    except Exception:
        pass
    _ws_size_cache["size"] = total
    _ws_size_cache["ts"] = now
    return total


@app.get("/api/stats")
async def get_stats() -> dict:
    version = _get_version_fast()

    agent_count = 0
    if OPENCLAW_CONFIG.exists():
        try:
            config = parse_json5(OPENCLAW_CONFIG.read_text())
            agent_count = len(config.get("agents", {}).get("list", []))
        except Exception:
            pass

    workspace_size = _get_workspace_size()
    gateway_running = await _check_gateway_fast()

    # Kanban summary
    kanban = _load_kanban()
    tasks = kanban.get("tasks", [])
    task_summary = {
        "total": len(tasks),
        "backlog": sum(1 for t in tasks if t.get("status") == "backlog"),
        "inProgress": sum(1 for t in tasks if t.get("status") == "in-progress"),
        "review": sum(1 for t in tasks if t.get("status") == "review"),
        "done": sum(1 for t in tasks if t.get("status") == "done"),
    }

    return {
        "version": version,
        "agentCount": agent_count,
        "workspaceSizeBytes": workspace_size,
        "workspaceSizeMB": round(workspace_size / (1024 * 1024), 2),
        "gatewayRunning": gateway_running,
        "tasks": task_summary,
    }


# ── System Health Metrics ───────────────────────────────────────────

@app.get("/api/health")
async def get_system_health() -> dict:
    """Get system health metrics: uptime, memory, disk, CPU load."""
    import psutil
    
    # Uptime
    try:
        with open("/proc/uptime", "r") as f:
            uptime_seconds = float(f.read().split()[0])
            uptime_str = _format_uptime(uptime_seconds)
    except Exception:
        uptime_str = "Unknown"
    
    # Memory
    try:
        mem = psutil.virtual_memory()
        memory_used = round(mem.used / (1024 * 1024 * 1024), 1)
        memory_total = round(mem.total / (1024 * 1024 * 1024), 1)
        memory_percent = mem.percent
    except Exception:
        memory_used = memory_total = memory_percent = 0
    
    # Disk usage for workspace
    try:
        disk = shutil.disk_usage(str(OPENCLAW_DIR))
        disk_used = round(disk.used / (1024 * 1024 * 1024), 1)
        disk_total = round(disk.total / (1024 * 1024 * 1024), 1)
        disk_percent = round((disk.used / disk.total) * 100, 1) if disk.total > 0 else 0
    except Exception:
        disk_used = disk_total = disk_percent = 0
    
    # CPU load (1, 5, 15 min averages)
    try:
        load1, load5, load15 = os.getloadavg()
    except Exception:
        load1 = load5 = load15 = 0
    
    # Process count
    try:
        proc_count = len(psutil.pids())
    except Exception:
        proc_count = 0
    
    # Gateway status
    gateway_url = get_gateway_url()
    gateway_online = await _check_gateway_fast()
    
    return {
        "uptime": uptime_str,
        "uptimeSeconds": uptime_seconds if 'uptime_seconds' in dir() else 0,
        "memory": {
            "usedGB": memory_used,
            "totalGB": memory_total,
            "percent": memory_percent,
        },
        "disk": {
            "usedGB": disk_used,
            "totalGB": disk_total,
            "percent": disk_percent,
        },
        "loadAvg": {
            "1min": round(load1, 2),
            "5min": round(load5, 2),
            "15min": round(load15, 2),
        },
        "processCount": proc_count,
        "gatewayOnline": gateway_online,
        "gatewayUrl": gateway_url,
    }


def _format_uptime(seconds: float) -> str:
    """Format seconds into human-readable uptime string."""
    days = int(seconds // 86400)
    hours = int((seconds % 86400) // 3600)
    minutes = int((seconds % 3600) // 60)
    
    if days > 0:
        return f"{days}d {hours}h"
    elif hours > 0:
        return f"{hours}h {minutes}m"
    else:
        return f"{minutes}m"


# ── Network Monitor (Gateway Log Tailing) ──────────────────────────

LOG_DIR = Path("/tmp/openclaw")

def get_today_log() -> Path:
    return LOG_DIR / f"openclaw-{datetime.now().strftime('%Y-%m-%d')}.log"


def parse_log_entry(raw: str) -> dict | None:
    try:
        obj = json.loads(raw)
    except json.JSONDecodeError:
        return None

    msg = obj.get("1", "") or obj.get("0", "")
    meta = obj.get("_meta", {})
    ts = obj.get("time", "")
    level = meta.get("logLevelName", "INFO")

    name_raw = obj.get("0", "")
    subsystem = ""
    try:
        parsed_name = json.loads(name_raw)
        subsystem = parsed_name.get("subsystem", "")
        msg = obj.get("1", "")
    except (json.JSONDecodeError, TypeError):
        subsystem = ""
        msg = name_raw

    if not msg:
        return None

    msg_lower = msg.lower()

    keywords = [
        "run start", "run end", "run complete", "run fail", "run error",
        "tool start", "tool end", "tool complete",
        "sendmessage", "send message", "telegram", "poll",
        "anthropic", "minimax", "openai", "provider",
        "model", "token", "usage",
        "inbound", "outbound", "webhook",
        "channel", "deliver",
        "http", "fetch", "request", "response",
        "error", "fail", "timeout", "retry",
        "stream", "sse",
        "bot api",
    ]

    is_interesting = any(kw in msg_lower for kw in keywords)
    if not is_interesting:
        return None

    category = "other"
    if any(x in msg_lower for x in ["anthropic", "minimax", "openai", "llm", "provider"]):
        category = "llm"
    elif any(x in msg_lower for x in ["telegram", "sendmessage", "bot api", "poll"]):
        category = "telegram"
    elif any(x in msg_lower for x in ["tool start", "tool end", "tool complete"]):
        category = "tool"
    elif any(x in msg_lower for x in ["run start", "run end", "run complete", "run fail"]):
        category = "agent"
    elif any(x in msg_lower for x in ["error", "fail", "timeout"]):
        category = "error"
    elif any(x in msg_lower for x in ["inbound", "outbound", "webhook", "channel", "deliver"]):
        category = "channel"

    return {
        "timestamp": ts,
        "level": level,
        "subsystem": subsystem,
        "message": msg[:500],
        "category": category,
        "raw": raw[:2000],
    }


@app.get("/api/network/log")
async def get_network_log(since_id: int = 0, limit: int = 100) -> dict:
    entries = [e for e in network_log if e["id"] > since_id]
    if len(entries) > limit:
        entries = entries[-limit:]
    return {"entries": entries, "paused": network_paused}


@app.post("/api/network/clear")
async def clear_network_log() -> dict:
    network_log.clear()
    return {"ok": True}


@app.post("/api/network/pause")
async def toggle_network_pause() -> dict:
    global network_paused
    network_paused = not network_paused
    return {"paused": network_paused}


@app.get("/api/network/tail")
async def tail_gateway_log(lines: int = 200) -> dict:
    global network_id_counter

    log_file = get_today_log()
    if not log_file.exists():
        return {"entries": [], "total": 0}

    all_lines = []
    try:
        with open(log_file, "r") as f:
            all_lines = f.readlines()
    except Exception:
        return {"entries": [], "total": 0}

    recent = all_lines[-lines:] if len(all_lines) > lines else all_lines

    entries = []
    for raw in recent:
        raw = raw.strip()
        if not raw:
            continue
        parsed = parse_log_entry(raw)
        if parsed and not network_paused:
            network_id_counter += 1
            parsed["id"] = network_id_counter
            entries.append(parsed)

    existing_msgs = set()
    for e in network_log:
        existing_msgs.add(e.get("timestamp", "") + e.get("message", "")[:100])

    new_entries = []
    for e in entries:
        key = e.get("timestamp", "") + e.get("message", "")[:100]
        if key not in existing_msgs:
            new_entries.append(e)
            network_log.append(e)

    return {"entries": list(network_log), "newCount": len(new_entries), "total": len(network_log)}


# ── Terminal ────────────────────────────────────────────────────────

@app.post("/api/terminal/exec")
async def terminal_exec(body: FileContent) -> dict:
    cmd = body.content.strip()
    if not cmd:
        return {"output": "", "code": 0}

    dangerous = ["rm -rf /", "mkfs", "dd if=", ":(){", "fork bomb"]
    for d in dangerous:
        if d in cmd.lower():
            return {"output": "⚠️ Command blocked for safety", "code": 1}

    try:
        proc = await asyncio.create_subprocess_shell(
            cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
            cwd=str(OPENCLAW_DIR),
        )
        stdout, _ = await asyncio.wait_for(proc.communicate(), timeout=30)
        output = stdout.decode("utf-8", errors="replace")
        return {"output": output[:50000], "code": proc.returncode or 0}
    except asyncio.TimeoutError:
        return {"output": "⚠️ Command timed out (30s limit)", "code": 124}
    except Exception as e:
        return {"output": f"Error: {e}", "code": 1}


# ── Security Panel ──────────────────────────────────────────────────

@app.get("/api/security")
async def get_security() -> dict:
    import re as _re
    from datetime import datetime, timedelta

    result = {
        "tailscale": {"status": "off", "hostname": "", "ip": "", "peers": 0},
        "ssh": {"recent": [], "failedLast24h": 0},
        "authEvents": [],
        "threats": {"failedSSH": 0, "blockedMessages": 0, "level": "low"},
    }

    # 1. Tailscale status
    try:
        proc = await asyncio.create_subprocess_exec(
            "tailscale", "status", "--json",
            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
        )
        stdout, _ = await asyncio.wait_for(proc.communicate(), timeout=5)
        if proc.returncode == 0:
            ts = json.loads(stdout.decode())
            self_node = ts.get("Self", {})
            peers = ts.get("Peer", {})
            online_peers = sum(1 for p in peers.values() if p.get("Online"))
            result["tailscale"] = {
                "status": "active" if ts.get("BackendState") == "Running" else "inactive",
                "hostname": self_node.get("HostName", ""),
                "ip": (self_node.get("TailscaleIPs") or [""])[0],
                "peers": online_peers,
                "totalPeers": len(peers),
            }
    except (FileNotFoundError, asyncio.TimeoutError):
        pass
    except Exception:
        pass

    # 2. SSH logs via journalctl
    try:
        proc = await asyncio.create_subprocess_exec(
            "journalctl", "-u", "sshd", "--no-pager", "-n", "50", "--output=json",
            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
        )
        stdout, _ = await asyncio.wait_for(proc.communicate(), timeout=5)
        if proc.returncode == 0:
            ssh_events = []
            for line in stdout.decode().strip().split("\n"):
                if not line.strip():
                    continue
                try:
                    entry = json.loads(line)
                    msg = entry.get("MESSAGE", "")
                    ts_us = int(entry.get("__REALTIME_TIMESTAMP", "0"))
                    ts_str = datetime.fromtimestamp(ts_us / 1_000_000).strftime("%Y-%m-%d %H:%M:%S") if ts_us else ""

                    user = ""
                    ip = ""
                    success = True

                    if "Accepted" in msg:
                        m = _re.search(r"Accepted \w+ for (\S+) from (\S+)", msg)
                        if m:
                            user, ip = m.group(1), m.group(2)
                    elif "Failed" in msg or "Invalid" in msg:
                        success = False
                        m = _re.search(r"(?:Failed|Invalid) \w+ for (?:invalid user )?(\S+) from (\S+)", msg)
                        if m:
                            user, ip = m.group(1), m.group(2)
                    elif "Connection closed" in msg or "Disconnected" in msg:
                        m = _re.search(r"from (\S+)", msg)
                        if m:
                            ip = m.group(1)
                    else:
                        continue

                    ssh_events.append({
                        "timestamp": ts_str,
                        "user": user,
                        "ip": ip,
                        "success": success,
                        "message": msg[:120],
                    })
                except (json.JSONDecodeError, ValueError):
                    continue

            result["ssh"]["recent"] = ssh_events[-30:]
    except (FileNotFoundError, asyncio.TimeoutError):
        pass
    except Exception:
        pass

    # Count failed SSH in last 24h via journalctl
    try:
        proc = await asyncio.create_subprocess_exec(
            "journalctl", "-u", "sshd", "--no-pager", "--since", "24 hours ago", "--output=cat",
            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
        )
        stdout, _ = await asyncio.wait_for(proc.communicate(), timeout=5)
        if proc.returncode == 0:
            text = stdout.decode()
            failed_count = text.lower().count("failed") + text.lower().count("invalid user")
            result["ssh"]["failedLast24h"] = failed_count
            result["threats"]["failedSSH"] = failed_count
    except Exception:
        pass

    # 3. OpenClaw auth events from gateway log
    today = datetime.now().strftime("%Y-%m-%d")
    log_path = Path(f"/tmp/openclaw/openclaw-{today}.log")
    blocked_count = 0
    if log_path.exists():
        try:
            text = log_path.read_text(errors="replace")
            auth_keywords = ["pairing", "allowfrom", "allowlist", "blocked", "rejected sender", "unauthorized", "dmPolicy", "ownerallowfrom", "deny sender"]
            auth_exclude = ["unhandled rejection", "fetch failed", "completion"]
            for line in text.split("\n")[-500:]:
                lower = line.lower()
                if any(kw in lower for kw in auth_keywords) and not any(ex in lower for ex in auth_exclude):
                    try:
                        entry = json.loads(line)
                        ts = entry.get("time", "")[:19].replace("T", " ")
                        msg_parts = []
                        for k in ["0", "1"]:
                            if k in entry:
                                msg_parts.append(str(entry[k])[:200])
                        msg = " ".join(msg_parts) if msg_parts else str(entry)[:200]

                        event_type = "info"
                        if any(w in lower for w in ["blocked", "reject", "denied", "unauthorized"]):
                            event_type = "blocked"
                            blocked_count += 1
                        elif any(w in lower for w in ["pairing"]):
                            event_type = "pairing"

                        result["authEvents"].append({
                            "timestamp": ts,
                            "type": event_type,
                            "message": msg[:200],
                        })
                    except json.JSONDecodeError:
                        pass
        except Exception:
            pass

    result["authEvents"] = result["authEvents"][-30:]
    result["threats"]["blockedMessages"] = blocked_count

    # Calculate threat level
    total_threats = result["threats"]["failedSSH"] + result["threats"]["blockedMessages"]
    if total_threats >= 20:
        result["threats"]["level"] = "high"
    elif total_threats >= 5:
        result["threats"]["level"] = "medium"
    else:
        result["threats"]["level"] = "low"

    return result


# ── Calendar (Cron Jobs) ───────────────────────────────────────────

async def _gateway_request(method: str, path: str, body: dict | None = None) -> dict:
    """Make an authenticated request to the OpenClaw gateway."""
    url = get_gateway_url()
    token = get_gateway_token()
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    if body:
        headers["Content-Type"] = "application/json"
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            if method == "GET":
                resp = await client.get(f"{url}{path}", headers=headers)
            elif method == "POST":
                resp = await client.post(f"{url}{path}", headers=headers, json=body)
            elif method == "PUT":
                resp = await client.put(f"{url}{path}", headers=headers, json=body)
            elif method == "DELETE":
                resp = await client.delete(f"{url}{path}", headers=headers)
            else:
                return {"error": f"Unsupported method: {method}"}
            if resp.status_code >= 400:
                return {"error": f"Gateway returned {resp.status_code}", "body": resp.text[:500]}
            return resp.json()
    except Exception as e:
        return {"error": str(e)}


CRON_JOBS_FILE = OPENCLAW_DIR / "cron" / "jobs.json"


def _parse_cron_schedule_desc(schedule: dict) -> str:
    """Human-readable schedule description. Safe parsing - never crashes."""
    try:
        kind = schedule.get("kind", "")
        if kind == "cron":
            expr = schedule.get("expr", "")
            parts = expr.split()
            if len(parts) >= 5:
                minute, hour, day_month, month, dow = parts[:5]
                if minute == "0" and hour.startswith("*/"):
                    try:
                        n = int(hour[2:])
                        return f"Every {n} hour{'s' if n > 1 else ''}"
                    except ValueError:
                        return expr
                if hour == "*" and minute.startswith("*/"):
                    try:
                        n = int(minute[2:])
                        return f"Every {n} minute{'s' if n > 1 else ''}"
                    except ValueError:
                        return expr
                if minute == "0" and hour.isdigit():
                    try:
                        h = int(hour)
                        ampm = "AM" if h < 12 else "PM"
                        h12 = h % 12 or 12
                        time_str = f"{h12}:00 {ampm}"
                        if day_month == "*" and month == "*":
                            if dow == "*":
                                return f"Daily at {time_str}"
                            dow_names = {"0": "Sun", "1": "Mon", "2": "Tue", "3": "Wed", "4": "Thu", "5": "Fri", "6": "Sat", "7": "Sun"}
                            day_name = dow_names.get(dow, dow)
                            return f"{day_name} at {time_str}"
                    except ValueError:
                        return expr
                return expr
            return expr
        elif kind == "every":
            ms = schedule.get("everyMs", 0)
            try:
                if ms >= 86400000:
                    days = ms // 86400000
                    return f"Every {days} day{'s' if days > 1 else ''}"
                elif ms >= 3600000:
                    hours = ms // 3600000
                    return f"Every {hours} hour{'s' if hours > 1 else ''}"
                elif ms >= 60000:
                    minutes = ms // 60000
                    return f"Every {minutes} minute{'s' if minutes > 1 else ''}"
                else:
                    seconds = ms // 1000
                    return f"Every {seconds} second{'s' if seconds > 1 else ''}"
            except Exception:
                return "Every (interval)"
        elif kind == "at":
            at = schedule.get("at", "")
            if not at:
                return "Once (time unknown)"
            try:
                d = datetime.fromisoformat(at.replace("Z", "+00:00"))
                if d.tzinfo is None:
                    d = d.replace(tzinfo=timezone.utc)
                ist = timezone(timedelta(hours=5, minutes=30))
                local = d.astimezone(ist)
                return f"Once at {local.strftime('%d/%m/%Y %I:%M %p')}"
            except Exception:
                return f"Once at {at}"
        return kind or "unknown"
    except Exception:
        return schedule.get("expr", "") or schedule.get("at", "") or "unknown"


def _get_cron_day_of_week(schedule: dict) -> list[int]:
    """Parse cron expression to get days of week (0=Sun..6=Sat). Returns empty for non-weekly."""
    kind = schedule.get("kind", "")
    if kind == "every":
        return list(range(7))  # Every day
    if kind == "at":
        at = schedule.get("at", "")
        try:
            from datetime import datetime as dt_
            d = dt_.fromisoformat(at.replace("Z", "+00:00"))
            return [d.weekday()]  # 0=Mon in Python
        except Exception:
            return []
    if kind == "cron":
        expr = schedule.get("expr", "")
        parts = expr.split()
        if len(parts) >= 5:
            dow_part = parts[4]
            if dow_part == "*":
                return list(range(7))
            days = []
            for seg in dow_part.split(","):
                seg = seg.strip()
                if "-" in seg:
                    try:
                        a, b = seg.split("-")
                        days.extend(range(int(a), int(b) + 1))
                    except ValueError:
                        pass
                else:
                    try:
                        days.append(int(seg))
                    except ValueError:
                        day_names = {"sun": 0, "mon": 1, "tue": 2, "wed": 3, "thu": 4, "fri": 5, "sat": 6}
                        if seg.lower()[:3] in day_names:
                            days.append(day_names[seg.lower()[:3]])
            return days
    return []


@app.get("/api/calendar/jobs")
async def get_calendar_jobs():
    """Get all cron jobs for calendar display."""
    if not CRON_JOBS_FILE.exists():
        return {"jobs": []}

    try:
        data = json.loads(CRON_JOBS_FILE.read_text())
    except (json.JSONDecodeError, PermissionError):
        return {"jobs": [], "error": "Failed to read cron jobs file"}

    jobs = data.get("jobs", [])
    for job in jobs:
        schedule = job.get("schedule", {})
        job["scheduleDesc"] = _parse_cron_schedule_desc(schedule)
        job["daysOfWeek"] = _get_cron_day_of_week(schedule)

    return {"jobs": jobs}


# ── Global Search (QMD) ────────────────────────────────────────────

@app.get("/api/search")
async def global_search(q: str = "", collections: str = "workspace,obsidian,memory-root,memory-dir", n: int = 10):
    """Search across all workspace memories/docs using QMD."""
    if not q or len(q) < 2:
        return {"results": [], "query": q}
    
    cols = [c.strip() for c in collections.split(",") if c.strip()]
    col_args = []
    for c in cols:
        col_args.extend(["-c", c])
    
    qmd = _find_qmd()
    if not qmd:
        return {"results": [], "query": q, "error": "qmd binary not found. Install qmd or set QMD_PATH env var."}

    try:
        proc = await asyncio.create_subprocess_exec(
            qmd, "search", q, *col_args, "-n", str(n), "--files",
            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=10)
        output = stdout.decode("utf-8", errors="replace").strip()
        
        results = []
        for line in output.split("\n"):
            line = line.strip()
            if not line:
                continue
            # Format: #color,score,qmd://collection/path
            parts = line.split(",", 2)
            if len(parts) >= 3:
                score = parts[1]
                qmd_uri = parts[2]
                # Parse qmd://collection/path
                if qmd_uri.startswith("qmd://"):
                    remainder = qmd_uri[6:]  # after qmd://
                    slash_idx = remainder.find("/")
                    if slash_idx >= 0:
                        collection = remainder[:slash_idx]
                        filepath = remainder[slash_idx + 1:]
                    else:
                        collection = remainder
                        filepath = ""
                    results.append({
                        "collection": collection,
                        "path": filepath,
                        "uri": qmd_uri,
                        "score": score,
                    })
        
        await _log_activity("search", q, details=f"{len(results)} results across {','.join(cols)}")
        return {"results": results, "query": q}
    except asyncio.TimeoutError:
        return {"results": [], "query": q, "error": "Search timed out"}
    except Exception as e:
        return {"results": [], "query": q, "error": str(e)}


@app.get("/api/search/snippet")
async def get_search_snippet(uri: str = "", lines: int = 20):
    """Get a snippet from a QMD document."""
    if not uri:
        raise HTTPException(status_code=400, detail="uri is required")
    
    qmd = _find_qmd()
    if not qmd:
        raise HTTPException(status_code=503, detail="qmd binary not found. Install qmd or set QMD_PATH env var.")

    try:
        proc = await asyncio.create_subprocess_exec(
            qmd, "get", uri, "-l", str(lines),
            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=5)
        content = stdout.decode("utf-8", errors="replace")
        return {"content": content, "uri": uri}
    except asyncio.TimeoutError:
        raise HTTPException(status_code=504, detail="Timed out")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── Activity Feed ──────────────────────────────────────────────────

ACTIVITY_FILE = OPENCLAW_DIR / "activity-feed.jsonl"

class ActivityEntry(BaseModel):
    action: str
    target: str = ""
    status: str = "success"
    duration_ms: int = 0
    agent: str = ""
    details: str = ""


def _parse_gateway_activity(limit: int = 200) -> list[dict]:
    """Parse gateway log for agent run events."""
    today = datetime.now().strftime("%Y-%m-%d")
    log_path = Path(f"/tmp/openclaw/openclaw-{today}.log")
    if not log_path.exists():
        return []

    entries = []
    try:
        with open(log_path, "r", errors="replace") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                except json.JSONDecodeError:
                    continue

                msg = str(obj.get("1", obj.get("0", "")))
                msg_lower = msg.lower()
                ts = obj.get("time", "")[:19].replace("T", " ")

                # Detect agent runs
                if "run start" in msg_lower or "run complete" in msg_lower or "run end" in msg_lower:
                    # Try to extract agent id
                    agent_id = ""
                    for aid in ["main", "atlas", "jupiter"]:
                        if aid in msg_lower:
                            agent_id = aid
                            break
                    action = "agent_run_start" if "start" in msg_lower else "agent_run_end"
                    entries.append({
                        "timestamp": ts,
                        "action": action,
                        "target": msg[:150],
                        "agent": agent_id,
                        "status": "success",
                        "details": "",
                        "duration_ms": 0,
                        "source": "gateway",
                    })
                # Detect tool calls
                elif "tool start" in msg_lower or "tool complete" in msg_lower:
                    agent_id = ""
                    for aid in ["main", "atlas", "jupiter"]:
                        if aid in msg_lower:
                            agent_id = aid
                            break
                    action = "tool_start" if "start" in msg_lower else "tool_end"
                    entries.append({
                        "timestamp": ts,
                        "action": action,
                        "target": msg[:150],
                        "agent": agent_id,
                        "status": "success",
                        "details": "",
                        "duration_ms": 0,
                        "source": "gateway",
                    })
                # Detect messages
                elif "sendmessage" in msg_lower or "deliver" in msg_lower:
                    entries.append({
                        "timestamp": ts,
                        "action": "message",
                        "target": msg[:150],
                        "agent": "",
                        "status": "success",
                        "details": "",
                        "duration_ms": 0,
                        "source": "gateway",
                    })
    except Exception:
        pass

    return entries[-limit:]


@app.get("/api/activity")
async def get_activity(limit: int = 50, agent: str = "", action: str = "", source: str = ""):
    """Get recent activity feed entries (dashboard + gateway logs)."""
    entries = []

    # Dashboard activity
    if ACTIVITY_FILE.exists() and source != "gateway":
        try:
            with open(ACTIVITY_FILE, "r") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        entry = json.loads(line)
                        entry.setdefault("source", "dashboard")
                        entries.append(entry)
                    except json.JSONDecodeError:
                        continue
        except Exception:
            pass

    # Gateway activity
    if source != "dashboard":
        gw_entries = _parse_gateway_activity(200)
        entries.extend(gw_entries)

    # Apply filters
    if agent:
        entries = [e for e in entries if e.get("agent") == agent]
    if action:
        entries = [e for e in entries if e.get("action") == action]

    # Sort by timestamp descending
    entries.sort(key=lambda e: e.get("timestamp", ""), reverse=True)
    total = len(entries)
    entries = entries[:limit]

    return {"entries": entries, "total": total}


@app.post("/api/activity")
async def log_activity(entry: ActivityEntry):
    """Log a new activity entry."""
    record = {
        "timestamp": datetime.now().isoformat(),
        **entry.model_dump(),
    }
    
    with open(ACTIVITY_FILE, "a") as f:
        f.write(json.dumps(record) + "\n")
    
    return record


# Activity feed is persistent — no delete endpoint


async def _log_activity(action: str, target: str, agent: str = "", status: str = "success", details: str = ""):
    record = {
        "timestamp": datetime.now().isoformat(),
        "action": action,
        "target": target,
        "agent": agent,
        "status": status,
        "details": details,
        "duration_ms": 0,
    }
    try:
        with open(ACTIVITY_FILE, "a") as f:
            f.write(json.dumps(record) + "\n")
    except Exception:
        pass


# ── Serve frontend ─────────────────────────────────────────────────

frontend_dir = Path(__file__).parent.parent / "frontend"
if (frontend_dir / "dist" / "index.html").exists():
    frontend_dir = frontend_dir / "dist"
app.mount("/", StaticFiles(directory=str(frontend_dir), html=True), name="frontend")
