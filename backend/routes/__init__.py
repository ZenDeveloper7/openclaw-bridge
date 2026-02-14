"""Routes package."""

from .files import setup_files_routes
from .kanban import setup_kanban_routes
from .agents import setup_agents_routes
from .network import setup_network_routes
from .terminal import setup_terminal_routes
from .calendar import setup_calendar_routes
from .security import setup_security_routes
from .activity import setup_activity_routes
from .config import setup_config_routes


def register_all_routes(app):
    """Register all route modules with the FastAPI app."""
    setup_files_routes(app)
    setup_kanban_routes(app)
    setup_agents_routes(app)
    setup_network_routes(app)
    setup_terminal_routes(app)
    setup_calendar_routes(app)
    setup_security_routes(app)
    setup_activity_routes(app)
    setup_config_routes(app)
