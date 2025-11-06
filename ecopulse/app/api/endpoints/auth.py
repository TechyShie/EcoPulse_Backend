from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from datetime import timedelta

from ...core.database import get_db
from ...core.security import create_access_token
from ...core.config import settings
from ...schemas.auth import Token, LoginRequest
from ...schemas.user import UserCreate, UserResponse
from ...services.auth import create_user, authenticate_user
from ...models.user import User
from ...api.dependencies import get_current_user

router = APIRouter()
security = HTTPBearer()

@router.post("/signup", response_model=UserResponse)
def signup(user_data: UserCreate, db: Session = Depends(get_db)):
    user = create_user(db, user_data)
    return user

@router.post("/login", response_model=Token)
def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    user = authenticate_user(db, login_data.email, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=str(user.id), expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/logout")
def logout():
    return {"message": "Successfully logged out"}

@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    print(f"🔍 DEBUG: Getting user info for user_id: {current_user.id}")
    print(f"🔍 DEBUG: User email: {current_user.email}")
    return current_user