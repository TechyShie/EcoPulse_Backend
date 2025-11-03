from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from app import models, schemas
from app.database import get_db
from app.core.security import get_current_user

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])


# -------------------------#
# Get dashboard stats
# -------------------------#
@router.get("/stats", response_model=schemas.DashboardStats)
def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    # Total emissions
    total_emissions = db.query(func.sum(models.Activity.carbon_output)).filter(
        models.Activity.user_id == current_user.id
    ).scalar() or 0.0

    # Eco score (simplified: lower emissions = higher score)
    eco_score = max(0, 100 - total_emissions * 10)

    # Weekly trend (last 7 days emissions)
    from datetime import datetime, timedelta
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    weekly_activities = db.query(models.Activity).filter(
        models.Activity.user_id == current_user.id,
        models.Activity.created_at >= seven_days_ago
    ).all()

    weekly_trend = [0.0] * 7
    for activity in weekly_activities:
        day_index = (datetime.utcnow() - activity.created_at).days
        if day_index < 7:
            weekly_trend[6 - day_index] += activity.carbon_output

    return {
        "total_emissions": total_emissions,
        "eco_score": eco_score,
        "weekly_trend": weekly_trend
    }


# -------------------------#
# Get recent activities
# -------------------------#
@router.get("/activities", response_model=List[schemas.ActivityResponse])
def get_recent_activities(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    activities = db.query(models.Activity).filter(models.Activity.user_id == current_user.id).order_by(
        models.Activity.created_at.desc()
    ).offset(skip).limit(limit).all()
    return activities
