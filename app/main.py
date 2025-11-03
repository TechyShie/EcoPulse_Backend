from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import (
    auth_router,
    activities_router,
    logs_router,
    dashboard_router,
    insights_router,
    leaderboard_router,
    profile_router,
    ai_router,
)
from app.services.ai_service import ai_service

app = FastAPI(title="EcoPulse API (SQLite)")

# CORS - adjust your frontend origin as needed
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    # Load AI model if available
    ai_service.load_model()

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    # Add any cleanup code here
    pass

app.include_router(auth_router)
app.include_router(activities_router)
app.include_router(logs_router)
app.include_router(dashboard_router)
app.include_router(insights_router)
app.include_router(leaderboard_router)
app.include_router(profile_router)
app.include_router(ai_router)

@app.get("/")
def root():
    return {"message": "EcoPulse API (SQLite) running"}
