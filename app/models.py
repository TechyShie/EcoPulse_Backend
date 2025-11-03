from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    role = Column(String, default="user")
    bio = Column(String, nullable=True)
    avatar = Column(String, nullable=True)
    refresh_token = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    activities = relationship("Activity", back_populates="user")


class Activity(Base):
    __tablename__ = "activities"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String, index=True)  # e.g. "Tree planting"
    category = Column(String, index=True)  # e.g. "transport", "food"
    description = Column(String, nullable=True)
    carbon_output = Column(Float, nullable=False)
    eco_points = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_archived = Column(Boolean, default=False)

    user = relationship("User", back_populates="activities")
