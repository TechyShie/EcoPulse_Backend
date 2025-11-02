from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import auth, activities

app = FastAPI(title="EcoPulse API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://eco-pulse-frontend.vercel.app", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(activities.router)

@app.get("/")
def root():
    return {"message": "EcoPulse backend connected successfully 🚀"}
