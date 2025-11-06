from pydantic import BaseModel
from typing import Optional, Dict
from datetime import datetime

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str

class CalculatePointsRequest(BaseModel):
    activity: str
    category: str
    details: Optional[str] = None
    date: Optional[datetime] = None

class CalculatePointsResponse(BaseModel):
    carbon_emission: float  # in kg CO2
    eco_points: int
    explanation: Optional[str] = None