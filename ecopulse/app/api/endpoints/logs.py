from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from ...core.database import get_db
from ...models.user import User
from ...models.log import Log
from ...schemas.log import LogCreate, LogResponse, LogUpdate
from ...api.dependencies import get_current_user

router = APIRouter()

@router.get("/", response_model=List[LogResponse])
def get_user_logs(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all logs for the current user"""
    try:
        logs = db.query(Log).filter(Log.user_id == current_user.id).order_by(Log.created_at.desc()).offset(skip).limit(limit).all()
        return logs
    except Exception as e:
        print(f"Error fetching logs: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error fetching user logs"
        )

@router.post("/", response_model=LogResponse)
def create_log(
    log_data: LogCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new eco activity log"""
    try:
        # Use points from frontend if provided, otherwise calculate based on emissions
        if log_data.points_earned is not None:
            points = log_data.points_earned
            print(f"🎯 Using frontend-provided points: {points}")
        else:
            # Fallback calculation (1 point per 100g CO2 saved)
            points = int(log_data.emissions_saved * 10)  # Convert kg to points (1kg = 1000g / 100 = 10 points)
            print(f"🔄 Calculating points from emissions: {log_data.emissions_saved}kg -> {points} points")
        
        # Create log data dict, excluding points_earned if it's None
        log_dict = log_data.dict(exclude_unset=True)
        
        db_log = Log(
            **log_dict,
            user_id=current_user.id,
            points_earned=points  # Always use the calculated points
        )
        
        # Update user's total emissions and eco score
        current_user.total_emissions_saved += int(log_data.emissions_saved * 1000)  # Convert kg to grams
        current_user.eco_score += points
        
        print(f"📊 User stats update - Emissions: +{log_data.emissions_saved}kg, Points: +{points}")
        
        db.add(db_log)
        db.commit()
        db.refresh(db_log)
        
        print(f"✅ Log created successfully: {db_log.id} with {db_log.points_earned} points")
        return db_log
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error creating log: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating log"
        )

@router.put("/{log_id}", response_model=LogResponse)
def update_log(
    log_id: int,
    log_data: LogUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update an existing log"""
    try:
        log = db.query(Log).filter(Log.id == log_id, Log.user_id == current_user.id).first()
        if not log:
            raise HTTPException(status_code=404, detail="Log not found")
        
        # Store old values for user stats adjustment
        old_emissions = log.emissions_saved
        old_points = log.points_earned
        
        # Update log fields
        update_data = log_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(log, field, value)
        
        # If emissions_saved was updated but points_earned wasn't, recalculate points
        if 'emissions_saved' in update_data and 'points_earned' not in update_data:
            log.points_earned = int(log.emissions_saved * 10)  # 1kg = 10 points
        
        # Update user stats
        current_user.total_emissions_saved -= int(old_emissions * 1000)  # Convert kg to grams
        current_user.eco_score -= old_points
        current_user.total_emissions_saved += int(log.emissions_saved * 1000)  # Convert kg to grams
        current_user.eco_score += log.points_earned
        
        db.commit()
        db.refresh(log)
        return log
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"Error updating log: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error updating log"
        )

@router.delete("/{log_id}")
def delete_log(
    log_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a log"""
    try:
        log = db.query(Log).filter(Log.id == log_id, Log.user_id == current_user.id).first()
        if not log:
            raise HTTPException(status_code=404, detail="Log not found")
        
        # Update user's totals (convert kg to grams for consistency)
        current_user.total_emissions_saved -= int(log.emissions_saved * 1000)
        current_user.eco_score -= log.points_earned
        
        db.delete(log)
        db.commit()
        return {"message": "Log deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"Error deleting log: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error deleting log"
        )