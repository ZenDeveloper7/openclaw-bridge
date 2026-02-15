"""Terminal execution API."""

import subprocess
import asyncio
import shlex
from pathlib import Path
from fastapi import HTTPException

from models import TerminalCommand


def setup_terminal_routes(app):
    """Register terminal routes."""
    
    @app.post("/api/terminal/exec")
    def exec_terminal(cmd: TerminalCommand):
        """Execute terminal command."""
        # Security: restrict to safe commands
        allowed_commands = [
            "ls", "pwd", "cat", "echo", "date", "uptime", "df", "free",
            "ps", "top", "htop", "git", "curl", "wget", "nano", "vim",
            "cd", "mkdir", "rm", "cp", "mv", "chmod", "chown",
            "docker", "kubectl", "systemctl", "journalctl",
            "python", "python3", "pip", "pip3", "node", "npm",
            "openclaw", "npx"
        ]
        
        # Fixed: Use shlex.split to safely parse command (no shell=True)
        command_list = shlex.split(cmd.command.strip())
        
        if not command_list:
            raise HTTPException(400, "Empty command")
        
        # Extract base command
        base_cmd = command_list[0]
        
        if base_cmd not in allowed_commands:
            raise HTTPException(403, f"Command not allowed: {base_cmd}")
        
        try:
            workdir = cmd.workdir or str(Path.home())
            # Fixed: Pass command as list, shell=False (default)
            result = subprocess.run(
                command_list,
                shell=False,
                cwd=workdir,
                capture_output=True,
                text=True,
                timeout=30
            )
            return {
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode
            }
        except subprocess.TimeoutExpired:
            raise HTTPException(408, "Command timed out")
        except Exception as e:
            raise HTTPException(500, str(e))
