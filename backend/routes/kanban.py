"""Kanban board API."""

import json
import random
from pathlib import Path
from fastapi import HTTPException

from config import get_kanban_file
from models import KanbanTask, KanbanBoard

# Random words for shareable task IDs
ADJECTIVES = ["brave", "cool", "swift", "happy", "calm", "bright", "bold", "eager", "gentle", "keen", "lively", "merry", "noble", "proud", "quick", "royal", "steady", "tender", "vivid", "wise", "young", "zesty", "amber", "azure", "cosmic", "dapper", "electric", "frosty", "golden", "honest", "iron", "jolly", "kind", "lemon", "mint", "neon", "olive", "pearl", "ruby", "silver", "topaz", "ultra", "violet", "warm", "xenon", "yellow", "zen"]

ANIMALS = ["lion", "tiger", "eagle", "wolf", "fox", "bear", "hawk", "owl", "deer", "fox", "whale", "dolphin", "raven", "snake", "jaguar", "panther", "cobra", "falcon", "phoenix", "dragon", "panda", "koala", "sloth", "otter", "seal", "penguin", "polar bear", "leopard", "cheetah", "gorilla", "chimpanzee", "elephant", "giraffe", "zebra", "hippo", "rhino", "buffalo", "moose", "elk", "bison", "pronghorn", "ibex", "chamois", "yak", "ox", "water buffalo", "gaur", "nilgai", "blackbuck", "sambar", "sika", "wapiti", "caribou"]

def _generate_task_id() -> str:
    """Generate a random word-based task ID."""
    adj = random.choice(ADJECTIVES).capitalize()
    animal = random.choice(ANIMALS).capitalize()
    return f"{adj}{animal}"


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
        # Generate random word-based ID if not provided
        task.id = task.id or _generate_task_id()
        data["tasks"].append(task.model_dump())
        _save_kanban(data)
        return task
    
    @app.put("/api/kanban/task/{task_id}")
    def update_task(task_id: str, task: KanbanTask):
        """Update task."""
        # Fixed: Validate task ID is not empty
        if not task_id or not task_id.strip():
            raise HTTPException(400, "Invalid task ID")
        
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
        # Fixed: Validate task ID is not empty
        if not task_id or not task_id.strip():
            raise HTTPException(400, "Invalid task ID")
        
        data = _load_kanban()
        data["tasks"] = [t for t in data["tasks"] if t["id"] != task_id]
        _save_kanban(data)
        return {"success": True}
    
    @app.put("/api/kanban/task/{task_id}/move")
    def move_task(task_id: str, body: dict):
        """Move task to column."""
        status = body.get("status", "")
        if not status:
            raise HTTPException(400, "Missing status")
        data = _load_kanban()
        for t in data["tasks"]:
            if t["id"] == task_id:
                t["status"] = status
                _save_kanban(data)
                return t
        raise HTTPException(404, "Task not found")
