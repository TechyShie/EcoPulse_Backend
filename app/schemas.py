from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr


# =======================
# USER SCHEMAS
# =======================

class UserBase(BaseModel):
    username: str
    email: EmailStr


class UserCreate(UserBase):
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(UserBase):
    id: int
    role: str
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


# =======================
# TOKEN SCHEMAS
# =======================

class Token(BaseModel):
    access_token: str
    token_type: str


class TokenWithRefresh(Token):
    refresh_token: str


# =======================
# ACTIVITY SCHEMAS
# =======================

class ActivityBase(BaseModel):
    name: str
    category: str
    description: Optional[str] = None


class ActivityCreate(ActivityBase):
    carbon_output: float
    # Optional structured inputs to compute emissions when provided
    distance: float | None = None
    quantity: float | None = None
    mode: str | None = None


class ActivityResponse(ActivityBase):
    id: int
    carbon_output: float
    eco_points: float | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


# =======================
# REFRESH AND LOGOUT SCHEMAS
# =======================

class RefreshRequest(BaseModel):
    refresh_token: str


class LogoutRequest(BaseModel):
    access_token: str
    refresh_token: str


# =======================
# DASHBOARD SCHEMAS
# =======================

class DashboardStats(BaseModel):
    total_emissions: float
    eco_score: float
    weekly_trend: list[float]


# =======================
# INSIGHTS SCHEMAS
# =======================

class WeeklyInsight(BaseModel):
    week: str
    emissions: float
    activities: int


class CategoryInsight(BaseModel):
    category: str
    total_emissions: float
    count: int


class MonthlySummary(BaseModel):
    month: str
    total_emissions: float
    eco_score: float
    activities_count: int


# =======================
# LEADERBOARD SCHEMAS
# =======================

class LeaderboardEntry(BaseModel):
    id: int
    full_name: str
    points: int
    eco_score: float


# =======================
# PROFILE SCHEMAS
# =======================

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    bio: Optional[str] = None
    avatar: Optional[str] = None


class UserProfile(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    bio: Optional[str] = None
    avatar: Optional[str] = None
    eco_score: float
    points: int
    created_at: datetime

    model_config = {"from_attributes": True}


class BadgeResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    icon: Optional[str] = None
    earned_at: datetime


class AchievementResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    points: int
    earned_at: datetime


# =======================
# AI SCHEMAS
# =======================

class AIChatRequest(BaseModel):
    message: str


class AIChatResponse(BaseModel):
    response: str


class CalculatePointsRequest(BaseModel):
    activity: str
    category: str
    carbon_emission: float


class CalculatePointsResponse(BaseModel):
    eco_points: float
    prediction_type: str  # "model" or "fallback"
    message: str
