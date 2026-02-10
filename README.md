# 🦞 OpenClaw Admin Dashboard

A web-based control board for the [OpenClaw](https://github.com/nicobailon/openclaw) AI gateway.

![Screenshot](https://via.placeholder.com/1200x600?text=OpenClaw+Dashboard+Screenshot)

## Features

- **📊 Dashboard** — Real-time overview of gateway status, agents, and tasks
- **📋 Kanban Board** — Drag-and-drop task management for agents
- **📅 Calendar + Timeline** — Visualize scheduled cron jobs
- **📁 File Explorer** — Browse `~/.openclaw` with image viewer, JSONL inspector, and inline editor
- **📊 Activity Feed** — Live stream of agent runs, tool calls, and messages
- **🤖 Agent Management** — Monitor agent sessions, models, and workspaces
- **🛡️ Security Panel** — Tailscale status, SSH logs, auth events, threat level
- **🔍 Global Search** — Full-text search across workspace via [QMD](https://github.com/nicobailon/qmd)

## Quick Start

```bash
# Clone
git clone https://github.com/nicobailon/openclaw-dashboard.git
cd openclaw-dashboard

# Set up Python environment
python3 -m venv backend/.venv
source backend/.venv/bin/activate
pip install -r requirements.txt

# Run
uvicorn backend.main:app --host 0.0.0.0 --port 8787
```

Open [http://localhost:8787](http://localhost:8787) in your browser.

## Configuration

All configuration is via environment variables:

| Variable | Default | Description |
|---|---|---|
| `OPENCLAW_DIR` | `~/.openclaw` | Path to your OpenClaw installation directory |
| `QMD_PATH` | auto-detect via `PATH` | Path to `qmd` binary for global search |
| `DASHBOARD_HOST` | `0.0.0.0` | Host to bind the server to |
| `DASHBOARD_PORT` | `8787` | Port to run the dashboard on |

Example:

```bash
OPENCLAW_DIR=/opt/openclaw DASHBOARD_PORT=9000 uvicorn backend.main:app --host 0.0.0.0 --port 9000
```

## Tech Stack

- **Backend:** Python / [FastAPI](https://fastapi.tiangolo.com/) / Uvicorn
- **Frontend:** Vanilla JavaScript — no build step, no framework, no node_modules
- **Search:** [QMD](https://github.com/nicobailon/qmd) (optional, for global search)

## Project Structure

```
├── backend/
│   └── main.py          # FastAPI application
├── frontend/
│   ├── index.html       # Single-page app shell
│   ├── dist/            # Served static files
│   └── src/
│       ├── app.js       # All frontend logic
│       └── style.css    # All styles
├── requirements.txt
└── README.md
```

## License

[MIT](LICENSE) © 2026 Zen
