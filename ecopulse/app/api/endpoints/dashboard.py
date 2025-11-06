from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta

from ...core.database import get_db
from ...models.user import User
from ...models.log import Log
from ...api.dependencies import get_current_user

router = APIRouter()

@router.get("/stats")
def get_dashboard_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Weekly trend data
    week_ago = datetime.utcnow() - timedelta(days=7)
    
    weekly_emissions = db.query(func.sum(Log.emissions_saved)).filter(
        Log.user_id == current_user.id,
        Log.activity_date >= week_ago
    ).scalar() or 0
    
    weekly_logs = db.query(Log).filter(
        Log.user_id == current_user.id,
        Log.activity_date >= week_ago
    ).count()
    
    return {
        "total_emissions_saved": current_user.total_emissions_saved,
        "eco_score": current_user.eco_score,
        "weekly_emissions_saved": weekly_emissions,
        "weekly_activity_count": weekly_logs,
        "user_rank": "Eco Warrior"  # Simplified for now
    }

@router.get("/activities")
def get_recent_activities(
    skip: int = 0,
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    activities = db.query(Log).filter(
        Log.user_id == current_user.id
    ).order_by(Log.activity_date.desc()).offset(skip).limit(limit).all()
    
    return activities