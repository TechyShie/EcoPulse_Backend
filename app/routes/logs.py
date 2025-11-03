from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app import models, schemas
from app.database import get_db
from app.core.security import get_current_user
from app.services.ai_service import ai_service
from app.utils.emissions_calculator import EmissionsCalculator

router = APIRouter(prefix="/api/logs", tags=["Logs"])


# -------------------------#
# Create new log
# -------------------------#
@router.post("/", response_model=schemas.ActivityResponse, status_code=status.HTTP_201_CREATED)
def create_log(
    activity: schemas.ActivityCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    # Optionally compute carbon_output if structured inputs are provided
    carbon_output = activity.carbon_output
    try:
        structured = {
            "category": activity.category,
            "activity": activity.name or (activity.description or ""),
            "distance": activity.distance,
            "quantity": activity.quantity,
            "mode": activity.mode,
        }
        # If any structured inputs are present, use emissions calculator
        if any([structured.get("distance"), structured.get("quantity"), structured.get("mode")]):
            carbon_output = EmissionsCalculator.calculate_emissions(structured)
    except Exception:
        # Fallback to provided carbon_output on any error
        carbon_output = activity.carbon_output

    # Compute eco points using AI service
    eco_points = ai_service.predict_eco_points(
        activity=activity.name or (activity.description or ""),
        category=activity.category,
        carbon_emission=float(carbon_output),
    )

    new_activity = models.Activity(
        name=activity.name,
        description=activity.description,
        category=activity.category,
        carbon_output=carbon_output,
        eco_points=eco_points,
        user_id=current_user.id,
    )
    db.add(new_activity)
    db.commit()
    db.refresh(new_activity)
    return new_activity


# -------------------------#
# Get all user logs
# -------------------------#
@router.get("/", response_model=List[schemas.ActivityResponse])
def get_logs(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    activities = db.query(models.Activity).filter(models.Activity.user_id == current_user.id).offset(skip).limit(limit).all()
    return activities


# -------------------------#
# Update a log
# -------------------------#
@router.put("/{id}", response_model=schemas.ActivityResponse)
def update_log(
    id: int,
    activity: schemas.ActivityCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    activity_db = db.query(models.Activity).filter(
        models.Activity.id == id, models.Activity.user_id == current_user.id
    ).first()

    if not activity_db:
        raise HTTPException(status_code=404, detail="Log not found")

    activity_db.name = activity.name
    activity_db.description = activity.description
    activity_db.category = activity.category
    # Optionally recompute carbon_output if structured inputs were supplied on update
    carbon_output = activity.carbon_output
    try:
        structured = {
            "category": activity.category,
            "activity": activity.name or (activity.description or ""),
            "distance": activity.distance,
            "quantity": activity.quantity,
            "mode": activity.mode,
        }
        if any([structured.get("distance"), structured.get("quantity"), structured.get("mode")]):
            carbon_output = EmissionsCalculator.calculate_emissions(structured)
    except Exception:
        carbon_output = activity.carbon_output

    activity_db.carbon_output = carbon_output
    # Recalculate eco points
    activity_db.eco_points = ai_service.predict_eco_points(
        activity=activity.name or (activity.description or ""),
        category=activity.category,
        carbon_emission=float(carbon_output),
    )

    db.commit()
    db.refresh(activity_db)
    return activity_db


# -------------------------#
# Delete a log
# -------------------------#
@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_log(
    id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    activity = db.query(models.Activity).filter(
        models.Activity.id == id, models.Activity.user_id == current_user.id
    ).first()

    if not activity:
        raise HTTPException(status_code=404, detail="Log not found")

    db.delete(activity)
    db.commit()
    # 204 No Content: return no body
    return None
