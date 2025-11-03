from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app import models, schemas
from app.database import get_db
from app.core.security import get_current_user
from app.services.ai_service import ai_service
from app.utils.emissions_calculator import EmissionsCalculator

router = APIRouter(prefix="/api/activities", tags=["Activities"])


# -------------------------
# Create new activity
# -------------------------
@router.post("/", response_model=schemas.ActivityResponse, status_code=status.HTTP_201_CREATED)
def create_activity(
    activity: schemas.ActivityCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    # Align behavior with Logs: optionally compute emissions and always compute eco_points
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

    eco_points = ai_service.predict_eco_points(
        activity=activity.name or (activity.description or ""),
        category=activity.category,
        carbon_emission=float(carbon_output),
    )

    new_activity = models.Activity(
        name=activity.name,
        category=activity.category,
        description=activity.description,
        carbon_output=carbon_output,
        eco_points=eco_points,
        user_id=current_user.id,
    )
    db.add(new_activity)
    db.commit()
    db.refresh(new_activity)
    return new_activity


# -------------------------
# Get all user activities
# -------------------------
@router.get("/", response_model=List[schemas.ActivityResponse])
def get_user_activities(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    activities = db.query(models.Activity).filter(models.Activity.user_id == current_user.id).all()
    return activities


# -------------------------
# Delete an activity
# -------------------------
@router.delete("/{activity_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_activity(
    activity_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    activity = db.query(models.Activity).filter(
        models.Activity.id == activity_id, models.Activity.user_id == current_user.id
    ).first()

    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")

    db.delete(activity)
    db.commit()
    # 204 No Content: return no body
    return None
