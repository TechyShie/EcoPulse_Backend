from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class LogBase(BaseModel):
    activity_type: str
    description: str
    emissions_saved: float
    points_earned: Optional[int] = None  # Make points_earned optional in base

class LogCreate(LogBase):
    points_earned: Optional[int] = None  # Allow points_earned to be sent from frontend

class LogUpdate(BaseModel):
    activity_type: Optional[str] = None
    description: Optional[str] = None
    emissions_saved: Optional[float] = None
    points_earned: Optional[int] = None  # Add points_earned to update

class LogResponse(LogBase):
    id: int
    user_id: int
    points_earned: int  # Required in response
    activity_date: datetime
    created_at: datetime

    class Config:
        orm_mode = True