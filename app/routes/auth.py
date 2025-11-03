from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta
from app import models, schemas
from app.database import get_db
from app.core.security import (
    create_access_token,
    create_refresh_token,
    verify_password,
    hash_password,  # ✅ fixed
    decode_token,
)
from app.core.dependencies import TOKEN_BLACKLIST

router = APIRouter(prefix="/api/auth", tags=["Auth"])

ACCESS_TOKEN_EXPIRE_MINUTES = 60


# -------------------------
# Register
# -------------------------
@router.post("/register", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: schemas.UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(models.User).filter(models.User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_pw = hash_password(user_data.password)  # ✅ use correct function name
    new_user = models.User(
        username=user_data.username,
        email=user_data.email,
        password=hashed_pw,
        role="user"
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


# -------------------------
# Login
# -------------------------
@router.post("/login", response_model=schemas.TokenWithRefresh)
def login(credentials: schemas.UserLogin, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == credentials.email).first()
    if not user or not verify_password(credentials.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    # ✅ pass subject instead of data
    access_token = create_access_token(str(user.id), expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    refresh_token = create_refresh_token(str(user.id))

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


# -------------------------
# Token refresh
# -------------------------
@router.post("/refresh", response_model=schemas.TokenWithRefresh)
def refresh_token(request: schemas.RefreshRequest, db: Session = Depends(get_db)):
    payload = decode_token(request.refresh_token, refresh=True)  # ✅ added refresh=True
    if not payload or "sub" not in payload:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    user_id = payload.get("sub")
    user = db.query(models.User).filter(models.User.id == int(user_id)).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    new_access_token = create_access_token(str(user.id), expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    new_refresh_token = create_refresh_token(str(user.id))
    return {"access_token": new_access_token, "refresh_token": new_refresh_token, "token_type": "bearer"}


# -------------------------
# Logout (invalidate access token)
# -------------------------
@router.post("/logout")
def logout(request: schemas.LogoutRequest, db: Session = Depends(get_db)):
    TOKEN_BLACKLIST.add(request.access_token)
    return {"msg": "logged out"}
