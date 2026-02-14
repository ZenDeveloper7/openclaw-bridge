"""Pydantic models for the dashboard API."""

from pydantic import BaseModel


class DashboardConfig(BaseModel):
    boardName: str = "Control Board"
    icon: str = "🦞"
    theme: str = "default"
    accentColor: str = "#f97316"


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
    status: str = "backlog"
    priority: str = "normal"
    tags: list[str] = []
    agent: str = "main"
    createdAt: str | None = None
    updatedAt: str | None = None


class KanbanBoard(BaseModel):
    tasks: list[KanbanTask] = []
    columns: list[str] = ["backlog", "in-progress", "review", "done"]


class JsonlLine(BaseModel):
    line: str
    data: dict


class ConfigPatch(BaseModel):
    boardName: str | None = None
    icon: str | None = None
    theme: str | None = None
    accentColor: str | None = None


class AgentInfo(BaseModel):
    id: str
    name: str
    status: str
    model: str | None = None
    sessionKey: str | None = None
    capabilities: list[str] = []


class TerminalCommand(BaseModel):
    command: str
    workdir: str | None = None


class ActivityEntry(BaseModel):
    id: str
    timestamp: str
    type: str
    content: str
    source: str | None = None
