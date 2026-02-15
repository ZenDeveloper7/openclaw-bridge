# Kanban Board — Usage Guide

The Kanban board lives inside the OpenClaw Admin Dashboard at `http://localhost:8787` under the **📋 Kanban** tab.

---

## Columns

| Column | Meaning |
|--------|---------|
| **📝 Backlog** | Tasks waiting to be picked up |
| **🔥 In Progress** | Actively being worked on |
| **👀 Review** | Done but needs verification or feedback |
| **✅ Done** | Completed |

## Creating a Task

1. Click **+ New Task** in the header, or the **+ Add task** button at the bottom of any column
2. Fill in the modal:
   - **Title** — What needs to be done (required)
   - **Description** — Details, notes, links
   - **Assign to** — `🦞 Poseidon`, `🛠️ Atlas`, or unassigned
   - **Priority** — Low / Normal / High / Urgent
   - **Status** — Which column it starts in
   - **Tags** — Comma-separated labels (e.g. `android, ui, bug`)
3. Click **Save Task**

## Moving Tasks (Drag & Drop)

- **Grab** any card and **drag** it to a different column
- Drop it in **Backlog**, **In Progress**, **Review**, or **Done**
- The status updates instantly and persists

## Editing a Task

- **Hover** over a card → click the **✏️** button
- Update any field in the modal
- Click **Save Task** to apply changes

## Deleting a Task

- Open the edit modal (✏️ on hover)
- Click **🗑️ Delete** at the bottom-left
- Confirm the deletion

## Priority Colors

Tasks show a colored left border based on priority:

- 🔴 **Urgent** — Red border
- 🟡 **High** — Yellow border
- ⚪ **Normal** — Subtle border
- 🔘 **Low** — Faint border

## Agent Badges

Each card shows who owns it:

- **🦞 Poseidon** — Cyan badge
- **🛠️ Atlas** — Orange badge
- **—** — Unassigned (gray)

## Data Storage

- All tasks are saved in `projects/admin-dashboard/kanban.json` (relative to project root)
- The file is plain JSON — you can edit it directly if needed
- Format:
```json
{
  "tasks": [
    {
      "id": "task-1234567890",
      "title": "Build feature X",
      "description": "Details here",
      "status": "in-progress",
      "agent": "atlas",
      "priority": "high",
      "tags": ["coding", "feature"],
      "created": "2026-02-06T13:45:47",
      "updated": "2026-02-06T14:00:00"
    }
  ],
  "columns": ["backlog", "in-progress", "review", "done"]
}
```

## API Endpoints

If you want to manage tasks programmatically (e.g. from agents or scripts):

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/kanban` | Get all tasks |
| `POST` | `/api/kanban/task` | Create a task |
| `PUT` | `/api/kanban/task/{id}` | Update a task |
| `DELETE` | `/api/kanban/task/{id}` | Delete a task |
| `PUT` | `/api/kanban/task/{id}/move` | Move to a different column |

### Examples

```bash
# Create a task
curl -X POST http://localhost:8787/api/kanban/task \
  -H 'Content-Type: application/json' \
  -d '{"id":"","title":"Fix login bug","status":"backlog","agent":"atlas","priority":"urgent","tags":["bug"]}'

# Move a task to in-progress
curl -X PUT http://localhost:8787/api/kanban/task/task-123/move \
  -H 'Content-Type: application/json' \
  -d '{"status":"in-progress"}'

# Delete a task
curl -X DELETE http://localhost:8787/api/kanban/task/task-123
```

## Auto-Add Tasks from Chat (Agent Instructions)

When Zen gives a task to any agent via Telegram (or any channel), the agent **must** automatically add it to the Kanban board. This keeps the board in sync with real work.

### Rules for Agents

1. **When you receive a task from Zen** → immediately `POST /api/kanban/task` to `http://localhost:8787`
2. **Set the fields correctly:**
   - `title` — Short, clear summary of the task
   - `description` — Any extra context Zen gave
   - `status` — `"in-progress"` if you're starting now, `"backlog"` if queued
   - `agent` — Your agent ID (`"main"` for Poseidon, `"atlas"` for Atlas)
   - `priority` — Infer from context (`"urgent"` if Zen says ASAP, `"high"` if important, `"normal"` otherwise)
   - `tags` — Relevant labels (e.g. `["android", "feature"]`, `["dashboard", "bug"]`)
3. **When you finish a task** → move it to `"done"` via `PUT /api/kanban/task/{id}/move`
4. **When starting work** → move from `"backlog"` to `"in-progress"`

### Example (agent adds a task)

```bash
curl -X POST http://localhost:8787/api/kanban/task \
  -H 'Content-Type: application/json' \
  -d '{
    "id": "",
    "title": "Add dark mode toggle",
    "description": "Zen wants a light/dark theme switch in the dashboard",
    "status": "in-progress",
    "agent": "atlas",
    "priority": "normal",
    "tags": ["dashboard", "ui"]
  }'
```

### What agents should track

| Event | Kanban Action |
|-------|--------------|
| Zen gives a new task | `POST` new task → `in-progress` or `backlog` |
| Agent starts working | Move to `in-progress` |
| Agent finishes | Move to `done` |
| Task needs Zen's input | Move to `review` |
| Task is blocked | Add `blocking` tag, keep in `backlog` |

**Key:** The Kanban board should always reflect reality. If you're working on it, it should be on the board.

## Dashboard Integration

The **📊 Dashboard** view shows:
- Task count stats (total, backlog, in-progress, done)
- **In Progress** panel on the right — quick view of active tasks
- Agent cards show which task each agent is working on

## Keyboard Shortcut

- **Ctrl+K** → Command Palette → type "Kanban" to jump to the board

---
