# app/models/__init__.py
from .user import User
from .log import Log
from .badge import Badge, UserBadge

# Export all models
__all__ = ["User", "Log", "Badge", "UserBadge"]