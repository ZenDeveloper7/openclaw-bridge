"""File operations API."""

import os
import re
import json
from pathlib import Path
from fastapi import HTTPException
from fastapi.responses import Response

from config import (
    OPENCLAW_DIR, parse_json5, _find_qmd, get_openclaw_dir
)
from models import FileContent, FileInfo, JsonlLine


def _safe_read(path: Path, max_size: int = 500_000) -> str:
    """Read file with size guard."""
    if path.stat().st_size > max_size:
        raise HTTPException(413, f"File too large (> {max_size // 1000}KB)")
    return path.read_text(encoding="utf-8")


def _list_dir(root: Path, rel_path: str = "") -> list[FileInfo]:
    """List directory contents."""
    target = root / rel_path if rel_path else root
    if not target.exists():
        raise HTTPException(404, "Path not found")
    if not target.is_dir():
        raise HTTPException(400, "Not a directory")
    
    try:
        entries = sorted(target.iterdir(), key=lambda p: (not p.is_dir(), p.name))
    except PermissionError:
        raise HTTPException(403, "Permission denied")
    
    result = []
    for entry in entries:
        name = entry.name
        if name.startswith("."):
            continue
        result.append(FileInfo(
            name=name,
            path=str(entry.relative_to(root)),
            is_dir=entry.is_dir(),
            size=entry.stat().st_size if entry.is_file() else None,
            modified=datetime.fromtimestamp(entry.stat().st_mtime).isoformat()
        ))
    return result


from datetime import datetime


def setup_files_routes(app):
    """Register file operation routes."""
    
    @app.get("/api/files")
    def list_files(path: str = ""):
        """List workspace files."""
        root = get_openclaw_dir() / "workspace-atlas"
        return _list_dir(root, path)
    
    @app.get("/api/files/read")
    def read_file(path: str):
        """Read file contents."""
        if ".." in path or path.startswith("/"):
            raise HTTPException(400, "Invalid path")
        root = get_openclaw_dir() / "workspace-atlas"
        file_path = root / path
        if not file_path.exists():
            raise HTTPException(404, "File not found")
        if file_path.is_dir():
            raise HTTPException(400, "Is a directory")
        
        content = _safe_read(file_path)
        return FileContent(content=content)
    
    @app.get("/api/files/image")
    def get_image(path: str):
        """Serve image file."""
        if ".." in path or path.startswith("/"):
            raise HTTPException(400, "Invalid path")
        root = get_openclaw_dir() / "workspace-atlas"
        file_path = root / path
        if not file_path.exists():
            raise HTTPException(404, "File not found")
        
        media_type = {
            ".png": "image/png",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".gif": "image/gif",
            ".webp": "image/webp"
        }.get(file_path.suffix.lower(), "application/octet-stream")
        
        return Response(content=file_path.read_bytes(), media_type=media_type)
    
    @app.get("/api/files/jsonl")
    def read_jsonl(path: str, limit: int = 100):
        """Read JSONL file."""
        if ".." in path or path.startswith("/"):
            raise HTTPException(400, "Invalid path")
        root = get_openclaw_dir()
        file_path = root / path
        if not file_path.exists():
            raise HTTPException(404, "File not found")
        
        lines = []
        with open(file_path, "r", encoding="utf-8") as f:
            for i, line in enumerate(f):
                if i >= limit:
                    break
                if line.strip():
                    try:
                        lines.append(json.loads(line))
                    except json.JSONDecodeError:
                        pass
        return lines
    
    @app.put("/api/files/jsonl/line")
    def append_jsonl(path: str, data: dict):
        """Append line to JSONL file."""
        if ".." in path or path.startswith("/"):
            raise HTTPException(400, "Invalid path")
        root = get_openclaw_dir()
        file_path = root / path
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(data) + "\n")
        return {"success": True}
    
    @app.put("/api/files/write")
    def write_file(path: str, content: str):
        """Write file."""
        if ".." in path or path.startswith("/"):
            raise HTTPException(400, "Invalid path")
        root = get_openclaw_dir()
        file_path = root / path
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content, encoding="utf-8")
        return {"success": True}
    
    @app.get("/api/files/search")
    def search_files(q: str, limit: int = 10):
        """Search files using qmd."""
        qmd_path = _find_qmd()
        if not qmd_path:
            raise HTTPException(503, "qmd not found")
        
        import subprocess
        try:
            result = subprocess.run(
                [qmd_path, "search", q, "-n", str(limit), "--workspace"],
                capture_output=True, text=True, timeout=30
            )
            return {"results": result.stdout.strip().split("\n") if result.stdout else []}
        except Exception as e:
            raise HTTPException(500, str(e))
