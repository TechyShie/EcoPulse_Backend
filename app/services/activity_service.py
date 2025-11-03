from sqlalchemy.orm import Session
from app import models, schemas
from datetime import datetime

def create_activity(user_id: int, activity_in: schemas.ActivityCreate, db: Session):
    activity = models.Activity(
        user_id=user_id,
        category=activity_in.category,
        description=activity_in.description,
        emissions_kg=activity_in.emissions_kg,
        created_at=datetime.utcnow(),
    )
    db.add(activity)
    db.commit()
    db.refresh(activity)
    return activity


def list_user_activities(user_id: int, db: Session, skip: int = 0, limit: int = 10):
    return (
        db.query(models.Activity)
        .filter(models.Activity.user_id == user_id, models.Activity.is_archived == False)
        .order_by(models.Activity.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
