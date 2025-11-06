from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

# Import your routers - FIXED IMPORT PATHS
from app.api.endpoints import auth, logs, dashboard, insights, leaderboard, profile, ai
from app.core.config import settings
from app.core.database import import_models

# Import models first
import_models()

# Create FastAPI app instance
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:8080", 
        "http://127.0.0.1:8080",
        "https://eco-pulse-frontend.vercel.app",
        "https://*.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["authentication"])
app.include_router(logs.router, prefix="/api/logs", tags=["logs"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["dashboard"])
app.include_router(insights.router, prefix="/api/insights", tags=["insights"])
app.include_router(leaderboard.router, prefix="/api/leaderboard", tags=["leaderboard"])
app.include_router(profile.router, prefix="/api/profile", tags=["profile"])
app.include_router(ai.router, prefix="/api/ai", tags=["ai"])

@app.get("/")
async def root():
    return {"message": "Welcome to EcoPulse API", "version": settings.VERSION}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/up")
async def up_check():
    return {"status": "up"}