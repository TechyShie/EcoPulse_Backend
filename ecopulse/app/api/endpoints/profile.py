from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ...core.database import get_db
from ...models.user import User
from ...models.badge import UserBadge, Badge
from ...schemas.user import UserUpdate, UserResponse
from ...api.dependencies import get_current_user

router = APIRouter()

@router.get("/", response_model=UserResponse)
def get_profile(current_user: User = Depends(get_current_user)):
    return current_user

@router.put("/", response_model=UserResponse)
def update_profile(
    user_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    for field, value in user_data.dict(exclude_unset=True).items():
        setattr(current_user, field, value)
    
    db.commit()
    db.refresh(current_user)
    return current_user

@router.get("/badges")
def get_user_badges(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    badges = db.query(UserBadge).filter(
        UserBadge.user_id == current_user.id
    ).join(Badge).all()
    
    return {
        "badges": [
            {
                "id": ub.badge.id,
                "name": ub.badge.name,
                "description": ub.badge.description,
                "icon_url": ub.badge.icon_url,
                "earned_at": ub.earned_at
            }
            for ub in badges
        ]
    }

@router.get("/achievements")
def get_user_achievements(current_user: User = Depends(get_current_user)):
    achievements = []
    
    if current_user.eco_score >= 1000:
        achievements.append("Eco Master")
    if current_user.total_emissions_saved >= 10000:
        achievements.append("Climate Hero")
    if current_user.eco_score >= 100:
        achievements.append("Green Starter")
    
    return {"achievements": achievements}