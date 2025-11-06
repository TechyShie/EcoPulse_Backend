from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ...core.database import get_db
from ...models.user import User
from ...api.dependencies import get_current_user

router = APIRouter()

@router.get("/")
def get_leaderboard(
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    ranked_users = db.query(User).filter(
        User.is_active == True
    ).order_by(
        User.eco_score.desc()
    ).offset(skip).limit(limit).all()
    
    leaderboard = []
    for rank, user in enumerate(ranked_users, start=1):
        leaderboard.append({
            "rank": rank + skip,
            "user_id": user.id,
            "full_name": user.full_name or "Anonymous User",
            "avatar_url": user.avatar_url,
            "eco_score": user.eco_score,
            "total_emissions_saved": user.total_emissions_saved,
            "is_current_user": user.id == current_user.id
        })
    
    return {
        "leaderboard": leaderboard,
        "current_user_rank": next(
            (i + 1 + skip for i, u in enumerate(ranked_users) if u.id == current_user.id),
            None
        )
    }