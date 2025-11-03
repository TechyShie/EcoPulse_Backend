from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app import models, schemas
from app.database import get_db
from app.core.security import get_current_user

router = APIRouter(prefix="/api/profile", tags=["Profile"])


# -------------------------#
# Get profile
# -------------------------#
@router.get("/", response_model=schemas.UserProfile)
def get_profile(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    # Calculate eco score and points
    from sqlalchemy import func
    stats = db.query(
        func.sum(models.Activity.carbon_output).label('total_emissions'),
        func.count(models.Activity.id).label('activity_count')
    ).filter(models.Activity.user_id == current_user.id).first()

    total_emissions = stats.total_emissions or 0.0
    activity_count = stats.activity_count or 0

    eco_score = max(0, 100 - total_emissions * 5)
    points = activity_count * 10 + max(0, 100 - total_emissions)

    return {
        "id": current_user.id,
        "full_name": current_user.full_name or "Anonymous",
        "email": current_user.email,
        "bio": current_user.bio,
        "avatar": current_user.avatar,
        "eco_score": eco_score,
        "points": int(points),
        "created_at": current_user.created_at
    }


# -------------------------#
# Update profile
# -------------------------#
@router.put("/", response_model=schemas.UserProfile)
def update_profile(
    user_update: schemas.UserUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    if user_update.full_name is not None:
        current_user.full_name = user_update.full_name
    if user_update.bio is not None:
        current_user.bio = user_update.bio
    if user_update.avatar is not None:
        current_user.avatar = user_update.avatar

    db.commit()
    db.refresh(current_user)

    # Return updated profile with stats
    return get_profile(db, current_user)


# -------------------------#
# Get badges
# -------------------------#
@router.get("/badges", response_model=List[schemas.BadgeResponse])
def get_badges(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    # Mock badges based on activity count and emissions
    from sqlalchemy import func
    stats = db.query(
        func.sum(models.Activity.carbon_output).label('total_emissions'),
        func.count(models.Activity.id).label('activity_count')
    ).filter(models.Activity.user_id == current_user.id).first()

    total_emissions = stats.total_emissions or 0.0
    activity_count = stats.activity_count or 0

    badges = []
    badge_id = 1

    if activity_count >= 1:
        badges.append({
            "id": badge_id,
            "name": "First Steps",
            "description": "Logged your first activity",
            "icon": "🌱",
            "earned_at": current_user.created_at
        })
        badge_id += 1

    if activity_count >= 10:
        badges.append({
            "id": badge_id,
            "name": "Eco Warrior",
            "description": "Logged 10 activities",
            "icon": "⚔️",
            "earned_at": current_user.created_at
        })
        badge_id += 1

    if total_emissions <= 50:
        badges.append({
            "id": badge_id,
            "name": "Low Impact",
            "description": "Kept emissions under 50 units",
            "icon": "🌍",
            "earned_at": current_user.created_at
        })

    return badges


# -------------------------#
# Get achievements
# -------------------------#
@router.get("/achievements", response_model=List[schemas.AchievementResponse])
def get_achievements(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    # Mock achievements based on activity count and emissions
    from sqlalchemy import func
    stats = db.query(
        func.sum(models.Activity.carbon_output).label('total_emissions'),
        func.count(models.Activity.id).label('activity_count')
    ).filter(models.Activity.user_id == current_user.id).first()

    total_emissions = stats.total_emissions or 0.0
    activity_count = stats.activity_count or 0

    achievements = []
    achievement_id = 1

    if activity_count >= 1:
        achievements.append({
            "id": achievement_id,
            "name": "Getting Started",
            "description": "Completed your first activity log",
            "points": 10,
            "earned_at": current_user.created_at
        })
        achievement_id += 1

    if activity_count >= 5:
        achievements.append({
            "id": achievement_id,
            "name": "Consistent Tracker",
            "description": "Logged 5 activities",
            "points": 25,
            "earned_at": current_user.created_at
        })
        achievement_id += 1

    if total_emissions <= 25:
        achievements.append({
            "id": achievement_id,
            "name": "Carbon Conscious",
            "description": "Maintained low carbon emissions",
            "points": 50,
            "earned_at": current_user.created_at
        })

    return achievements
