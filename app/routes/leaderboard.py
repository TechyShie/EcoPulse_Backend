from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from app import models, schemas
from app.database import get_db
from app.core.security import get_current_user

router = APIRouter(prefix="/api/leaderboard", tags=["Leaderboard"])


# -------------------------#
# Get leaderboard
# -------------------------#
@router.get("/", response_model=List[schemas.LeaderboardEntry])
def get_leaderboard(
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    # Calculate points and eco score for each user
    leaderboard_data = db.query(
        models.User.id,
        models.User.full_name,
        func.sum(models.Activity.carbon_output).label('total_emissions'),
        func.count(models.Activity.id).label('activity_count')
    ).outerjoin(models.Activity).group_by(models.User.id, models.User.full_name).order_by(
        func.sum(models.Activity.carbon_output).asc()  # Lower emissions = higher rank
    ).limit(limit).all()

    leaderboard = []
    for user_id, full_name, total_emissions, activity_count in leaderboard_data:
        total_emissions = total_emissions or 0.0
        activity_count = activity_count or 0

        # Calculate points (simplified: more activities = more points, lower emissions = more points)
        points = activity_count * 10 + max(0, 100 - total_emissions)
        eco_score = max(0, 100 - total_emissions * 5)

        leaderboard.append({
            "id": user_id,
            "full_name": full_name or "Anonymous",
            "points": int(points),
            "eco_score": eco_score
        })

    return leaderboard
