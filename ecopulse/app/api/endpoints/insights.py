from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from datetime import datetime, timedelta

from ...core.database import get_db
from ...models.user import User
from ...models.log import Log
from ...api.dependencies import get_current_user

router = APIRouter()

@router.get("/weekly")
def get_weekly_insights(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Get data for the last 7 days
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=7)
    
    daily_data = db.query(
        func.date(Log.activity_date).label('date'),
        func.sum(Log.emissions_saved).label('emissions_saved'),
        func.count(Log.id).label('activity_count')
    ).filter(
        Log.user_id == current_user.id,
        Log.activity_date >= start_date,
        Log.activity_date <= end_date
    ).group_by(func.date(Log.activity_date)).all()
    
    return {
        "daily_data": [
            {
                "date": str(data.date),
                "emissions_saved": float(data.emissions_saved or 0),
                "activity_count": data.activity_count
            }
            for data in daily_data
        ]
    }

@router.get("/categories")
def get_category_distribution(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    category_data = db.query(
        Log.activity_type,
        func.sum(Log.emissions_saved).label('total_emissions'),
        func.count(Log.id).label('activity_count')
    ).filter(
        Log.user_id == current_user.id
    ).group_by(Log.activity_type).all()
    
    return {
        "categories": [
            {
                "activity_type": data.activity_type,
                "total_emissions": float(data.total_emissions or 0),
                "activity_count": data.activity_count
            }
            for data in category_data
        ]
    }

@router.get("/summary")
def get_monthly_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    current_month = datetime.utcnow().month
    current_year = datetime.utcnow().year
    
    monthly_data = db.query(
        func.sum(Log.emissions_saved).label('monthly_emissions'),
        func.count(Log.id).label('monthly_activities')
    ).filter(
        Log.user_id == current_user.id,
        extract('month', Log.activity_date) == current_month,
        extract('year', Log.activity_date) == current_year
    ).first()
    
    return {
        "monthly_emissions_saved": float(monthly_data.monthly_emissions or 0),
        "monthly_activities": monthly_data.monthly_activities or 0,
        "month": current_month,
        "year": current_year
    }