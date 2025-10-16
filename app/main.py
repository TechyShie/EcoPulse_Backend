from fastapi import FastAPI
from app.routes import auth, activities

app = FastAPI(title="EcoPulse API")

app.include_router(auth.router)
app.include_router(activities.router)

@app.get("/")
def root():
    return {"message": "EcoPulse backend connected successfully 🚀"}
