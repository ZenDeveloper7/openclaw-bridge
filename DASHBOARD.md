# DASHBOARD.md — OpenClaw Admin Dashboard

> Control board for monitoring and managing OpenClaw agents, tasks, and system health.

---

## Architecture

```
admin-dashboard/
├── backend/           # FastAPI (Python 3.14, uvicorn)
│   ├── main.py        # App entry, CORS, static mount
│   ├── config.py      # Paths, constants, helpers
│   ├── models.py      # Pydantic models
│   └── routes/        # API route modules
│       ├── __init__.py    # Route registration
│       ├── agents.py      # Agent info (reads disk directly)
│       ├── calendar.py    # Cron jobs (reads disk directly)
│       ├── activity.py    # Activity log (reads disk directly)
│       ├── kanban.py      # Kanban board (JSON file)
│       ├── files.py       # File operations + JSONL viewer
│       ├── config.py      # Dashboard config (theme, name)
│       ├── security.py    # System health + stats
│       ├── network.py     # Network monitor (SSE)
│       └── terminal.py    # Terminal execution
└── frontend/          # Vanilla JS (no build step)
    ├── index.html     # Main HTML with all views
    ├── src/
    │   ├── app.js     # All frontend logic (~2300 lines)
    │   └── style.css  # All styles
    └── dist/          # Mirror of above (keep synced)
```

## How to Run

```bash
cd ~/.openclaw/projects/admin-dashboard
source backend/.venv/bin/activate
cd backend
uvicorn main:app --host 0.0.0.0 --port 8787
```

Kill before restart: `pkill -f "uvicorn main:app"`

Port: **8787**  
Frontend served by FastAPI's StaticFiles from `frontend/` directory.

## Data Flow

**Key insight:** The backend reads OpenClaw data **directly from disk** (not via HTTP API or CLI). This makes responses ~15ms instead of ~3s.

| Data | Source File |
|------|------------|
| Sessions/Agents | `~/.openclaw/agents/*/sessions/sessions.json` |
| Cron Jobs | `~/.openclaw/cron/jobs.json` |
| Kanban Tasks | `~/.openclaw/projects/admin-dashboard/kanban.json` |
| Dashboard Config | `~/.openclaw/dashboard-config.json` |
| OpenClaw Config | `~/.openclaw/openclaw.json` |

**Agent "active" = session updated in last 30 minutes.**

---

## API Endpoints

### Dashboard & Health

| Method | Path | Description | Response |
|--------|------|-------------|----------|
| GET | `/api/stats` | Dashboard stats | `{agents, tasks: {total, backlog, in-progress, review, done}, workspaceSize}` |
| GET | `/api/health` | System health | `{uptime, memory: {usedGB, totalGB, percent}, disk: {...}, loadAvg, processCount, gatewayOnline}` |

### Agents

| Method | Path | Description | Response |
|--------|------|-------------|----------|
| GET | `/api/agents` | List agents | `[{id, name, status, model, sessionKey, messageCount, updatedAt, ageMs}]` |

### Calendar (Cron Jobs)

| Method | Path | Description | Response |
|--------|------|-------------|----------|
| GET | `/api/calendar/jobs` | List cron jobs | `[{id, name, schedule: {kind, expr, tz}, scheduleDesc, nextRun, lastRun, status, sessionTarget, agent}]` |

### Activity

| Method | Path | Description | Response |
|--------|------|-------------|----------|
| GET | `/api/activity?limit=50` | Recent activity | `[{id, timestamp, type, content, source, agent, model, updatedAt}]` |
| POST | `/api/activity` | Log custom entry | echo back |

### Kanban

| Method | Path | Description | Response |
|--------|------|-------------|----------|
| GET | `/api/kanban` | Get board | `{tasks: [...], columns: [...]}` |
| POST | `/api/kanban/task` | Create task | KanbanTask |
| PUT | `/api/kanban/task/{id}` | Update task | KanbanTask |
| DELETE | `/api/kanban/task/{id}` | Delete task | `{success}` |
| PUT | `/api/kanban/task/{id}/move` | Move task (body: `{status}`) | task |

### Files & Config

| Method | Path | Description | Response |
|--------|------|-------------|----------|
| GET | `/api/files?path=` | List directory | `[{name, path, is_dir, size, modified}]` |
| GET | `/api/files/read?path=` | Read file | `{content}` |
| PUT | `/api/files/write?path=` | Write file | `{success}` |
| GET | `/api/files/jsonl?path=&offset=0&limit=100` | Read JSONL | `{lines: [{index, data, raw}], total}` |
| GET | `/api/files/image?path=` | Serve image | binary |
| GET | `/api/files/search?q=&limit=10` | Search via QMD | `{results}` |
| GET | `/api/openclaw/config` | Read openclaw.json | Full JSON config |
| PUT | `/api/openclaw/config` | Save openclaw.json | `{success}` |
| GET | `/api/dashboard/config` | Get dashboard config | `{boardName, icon, theme, accentColor}` |
| POST | `/api/dashboard/config` | Update config | config |

### Security

| Method | Path | Description | Response |
|--------|------|-------------|----------|
| GET | `/api/security` | Security info | `{sshHardened, firewallEnabled, recentLogins, openclawVersion, workspaceSize}` |

### Terminal

| Method | Path | Description | Response |
|--------|------|-------------|----------|
| POST | `/api/terminal/exec` | Run command (body: `{command, workdir}`) | `{stdout, stderr, returncode}` |

---

## Frontend Views

| View | Nav Button | Function | APIs Called |
|------|-----------|----------|------------|
| Dashboard | 📊 Dashboard | `loadDashboard()` | `/api/stats`, `/api/health`, `/api/agents`, `/api/kanban` |
| Kanban | 📋 Kanban | `loadKanban()` | `/api/kanban` |
| Agents | 🤖 Agents | `loadAgents()` | `/api/agents` |
| Subagents | 🤖 Subagents | `loadSubagents()` | `/api/sessions` |
| Calendar | 📅 Calendar | `loadCalendar()` | `/api/calendar/jobs` |
| Config | ⚙️ Config | `loadConfig()` | `/api/openclaw/config` |
| Activity | 📊 Activity | `loadActivity()` | `/api/activity` |
| Security | 🛡️ Security | `loadSecurity()` | `/api/security` |

### Special Views (not in nav)
- **Editor** (`view-editor`) — File editor with markdown preview, opened via `openFile(path)`
- **JSONL Viewer** (`view-jsonl`) — JSONL browser with search/filter/pagination, opened via `openJsonl(path)`
- **Config Editor** — Editable openclaw.json with save button, syntax highlighting via textarea

---

| Agent cards | Green/gray status dot, model name, last active time, subtle session key | `renderAgentCard()` |
| Calendar filter | Agent dropdown filter, cron day-of-week detection | `calAgentFilter`, `parseCronDays()` |
| Activity feed | Shows agent emoji, session type icon, model, IST timestamps | `renderActivity()` |
| Config view | Editable openclaw.json with save button | `/api/openclaw/config` |
| JSONL backend | Returns `{lines: [{index, data, raw}], total}` with offset pagination | `/api/files/jsonl` |
| Timezone | All dates/times in IST (Asia/Calcutta) | `formatIST()` |
| Stats endpoint | Returns version, gatewayRunning, agentCount, workspaceSizeMB | `/api/stats` |
| Agent roles | `main: Executive Assistant`, `atlas: Coding Specialist`, `jupiter: Finance Analyst` | `AGENT_ROLES` |

| Function | Purpose |
|----------|---------|
| `formatIST(ts)` | Format any timestamp in IST (Asia/Calcutta) |
| `parseCronDays(cronExpr)` | Parse cron days-of-week for calendar display |
| `getAgentEmoji(id)` | Returns emoji for agent (🦞 main, 🛠️ atlas, 💰 jupiter) |
| `getAgentLabel(id)` | Returns "emoji name" string |
| `toast(msg, type)` | Toast notification |
| `openPalette()` | Command palette (Ctrl+K) |

## Subagents View
Shows all isolated agent sessions including:
- **Main agents** (main, atlas, jupiter) with agent roles
- **Subagents** (spawned runs) with model, token usage, channel, last active
- **Cron jobs** (scheduled tasks) with schedule description, next run, last run

Display cards with agent emoji, session ID, model, token usage stats, and time since last activity.

| Agent roles | `main: Executive Assistant`, `atlas: Coding Specialist`, `jupiter: Finance Analyst` | `AGENT_ROLES` |
| Subagents view | Shows main agents, subagents, cron jobs with token stats | `/api/sessions` |

---

## Themes

6 themes: `default`, `oled`, `light`, `nord`, `dracula`, `matrix`  
Custom accent color picker available in settings.

## Known Issues

- JSONL viewer treats non-JSONL files (like kanban.json) as line-per-line which breaks
- Security panel expects threat/tailscale/SSH data that the backend doesn't fully provide
- Network monitor is placeholder (no actual traffic capture)

---

## Recent Fixes (Feb 2026)

| Date | Fix |
|------|-----|
| Feb 15 | Added `/api/openclaw/config` endpoint for editable config |
| Feb 15 | Fixed activity feed to show human-readable time (e.g., "2h 0m ago") |
| Feb 15 | Updated stats endpoint with version, gatewayRunning, agentCount, workspaceSizeMB |
| Feb 15 | Added agent roles (main=Executive, atlas=Coding, jupiter=Finance) |
| Feb 15 | Fixed calendar filter data binding (was `data.jobs`, now direct array) |
| Feb 15 | Fixed JSONL backend to return `{lines, total}` with pagination |

---

*Updated: Feb 15, 2026*
