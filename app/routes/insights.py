from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from typing import List
from datetime import datetime, timedelta
from app import models, schemas
from app.database import get_db
from app.core.security import get_current_user

router = APIRouter(prefix="/api/insights", tags=["Insights"])


# -------------------------#
# Get weekly insights
# -------------------------#
@router.get("/weekly", response_model=List[schemas.WeeklyInsight])
def get_weekly_insights(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    # Get last 4 weeks
    insights = []
    for i in range(4):
        week_start = datetime.utcnow() - timedelta(weeks=i+1)
        week_end = datetime.utcnow() - timedelta(weeks=i)

        weekly_data = db.query(
            func.sum(models.Activity.carbon_output),
            func.count(models.Activity.id)
        ).filter(
            models.Activity.user_id == current_user.id,
            models.Activity.created_at >= week_start,
            models.Activity.created_at < week_end
        ).first()

        emissions = weekly_data[0] or 0.0 if weekly_data else 0.0
        activities = weekly_data[1] or 0 if weekly_data else 0

        week_str = f"Week {4-i}"
        insights.append({
            "week": week_str,
            "emissions": emissions,
            "activities": activities
        })

    return insights


# -------------------------#
# Get category insights
# -------------------------#
@router.get("/categories", response_model=List[schemas.CategoryInsight])
def get_category_insights(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    category_data = db.query(
        models.Activity.category,
        func.sum(models.Activity.carbon_output).label('total_emissions'),
        func.count(models.Activity.id).label('count')
    ).filter(
        models.Activity.user_id == current_user.id,
        models.Activity.category.isnot(None)
    ).group_by(models.Activity.category).all()

    insights = []
    for category, total_emissions, count in category_data:
        insights.append({
            "category": category,
            "total_emissions": total_emissions,
            "count": count
        })

    return insights


# -------------------------#
# Get monthly summary
# -------------------------#
@router.get("/summary", response_model=schemas.MonthlySummary)
def get_monthly_summary(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    current_month = datetime.utcnow().replace(day=1)

    monthly_data = db.query(
        func.sum(models.Activity.carbon_output).label('total_emissions'),
        func.count(models.Activity.id).label('activities_count')
    ).filter(
        models.Activity.user_id == current_user.id,
        extract('year', models.Activity.created_at) == current_month.year,
        extract('month', models.Activity.created_at) == current_month.month
    ).first()

    total_emissions = monthly_data[0] or 0.0 if monthly_data else 0.0
    activities_count = monthly_data[1] or 0 if monthly_data else 0
    eco_score = max(0, 100 - total_emissions * 5)  # Simplified eco score

    return {
        "month": current_month.strftime("%B %Y"),
        "total_emissions": total_emissions,
        "eco_score": eco_score,
        "activities_count": activities_count
    }
