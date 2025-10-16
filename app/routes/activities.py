from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app import models, schemas
from app.database import get_db
from app.core.dependencies import get_current_user

router = APIRouter(prefix="/activities", tags=["Activities"])

@router.post("/", response_model=schemas.ActivityResponse)
def create_activity(activity: schemas.ActivityCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    new_activity = models.Activity(
        description=activity.description,
        category=activity.category,
        carbon_emission=activity.carbon_emission,
        owner=current_user
    )
    db.add(new_activity)
    db.commit()
    db.refresh(new_activity)
    return new_activity

@router.get("/", response_model=List[schemas.ActivityResponse])
def get_activities(skip: int = 0, limit: int = 10, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    activities = db.query(models.Activity).filter(models.Activity.user_id == current_user.id).offset(skip).limit(limit).all()
    return activities

@router.get("/{id}", response_model=schemas.ActivityResponse)
def get_activity(id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    activity = db.query(models.Activity).filter(models.Activity.id == id, models.Activity.user_id == current_user.id).first()
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    return activity

@router.put("/{id}", response_model=schemas.ActivityResponse)
def update_activity(id: int, updated: schemas.ActivityCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    activity = db.query(models.Activity).filter(models.Activity.id == id, models.Activity.user_id == current_user.id).first()
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    activity.description = updated.description
    activity.category = updated.category
    activity.carbon_emission = updated.carbon_emission
    db.commit()
    db.refresh(activity)
    return activity

@router.delete("/{id}")
def delete_activity(id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    activity = db.query(models.Activity).filter(models.Activity.id == id, models.Activity.user_id == current_user.id).first()
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    db.delete(activity)
    db.commit()
    return {"message": "Activity deleted successfully"}
