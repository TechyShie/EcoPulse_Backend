# Import all routers to make them accessible
from .auth import router as auth_router
from .logs import router as logs_router
from .dashboard import router as dashboard_router
from .insights import router as insights_router
from .leaderboard import router as leaderboard_router
from .profile import router as profile_router
from .ai import router as ai_router

# Export all routers
__all__ = [
    "auth_router",
    "logs_router", 
    "dashboard_router",
    "insights_router",
    "leaderboard_router",
    "profile_router",
    "ai_router"
]