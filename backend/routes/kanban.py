"""Kanban board API."""

import json
from pathlib import Path
from fastapi import HTTPException

from config import get_kanban_file
from models import KanbanTask, KanbanBoard


def _load_kanban() -> dict:
    """Load kanban data from file."""
    kanban_file = get_kanban_file()
    if kanban_file.exists():
        try:
            return json.loads(kanban_file.read_text())
        except Exception:
            pass
    return {"tasks": [], "columns": ["backlog", "in-progress", "review", "done"]}


def _save_kanban(data: dict):
    """Save kanban data to file."""
    kanban_file = get_kanban_file()
    kanban_file.write_text(json.dumps(data, indent=2))


def setup_kanban_routes(app):
    """Register kanban routes."""
    
    @app.get("/api/kanban")
    def get_kanban():
        """Get kanban board."""
        return _load_kanban()
    
    @app.post("/api/kanban/task")
    def create_task(task: KanbanTask):
        """Create new task."""
        data = _load_kanban()
        task.id = task.id or f"task-{len(data['tasks']) + 1}"
        data["tasks"].append(task.model_dump())
        _save_kanban(data)
        return task
    
    @app.put("/api/kanban/task/{task_id}")
    def update_task(task_id: str, task: KanbanTask):
        """Update task."""
        data = _load_kanban()
        for i, t in enumerate(data["tasks"]):
            if t["id"] == task_id:
                task.id = task_id
                data["tasks"][i] = task.model_dump()
                _save_kanban(data)
                return task
        raise HTTPException(404, "Task not found")
    
    @app.delete("/api/kanban/task/{task_id}")
    def delete_task(task_id: str):
        """Delete task."""
        data = _load_kanban()
        data["tasks"] = [t for t in data["tasks"] if t["id"] != task_id]
        _save_kanban(data)
        return {"success": True}
    
    @app.put("/api/kanban/task/{task_id}/move")
    def move_task(task_id: str, status: str):
        """Move task to column."""
        data = _load_kanban()
        for t in data["tasks"]:
            if t["id"] == task_id:
                t["status"] = status
                _save_kanban(data)
                return t
        raise HTTPException(404, "Task not found")
