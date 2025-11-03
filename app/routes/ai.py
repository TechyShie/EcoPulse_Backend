from fastapi import APIRouter, Depends, HTTPException
from app import schemas
from app.core.security import get_current_user
from app import models
from app.services.ai_service import ai_service
from app.utils.emissions_calculator import EmissionsCalculator

router = APIRouter(prefix="/api/ai", tags=["AI Assistant"])


# -------------------------#
# Chat with AI
# -------------------------#
@router.post("/chat", response_model=schemas.AIChatResponse)
async def chat_with_ai(
    request: schemas.AIChatRequest,
    current_user: models.User = Depends(get_current_user),
):
    # Use AI for general eco-related responses
    message = request.message

    # Optional: Extract activity information from message (simplified parsing) for context
    activity = None
    category = None
    carbon_emission = None
    eco_points = None

    message_lower = message.lower()
    if "driving" in message_lower or "car" in message_lower:
        activity = "driving"
        category = "Transportation"
        carbon_emission = 15.0
    elif "flight" in message_lower or "flying" in message_lower:
        activity = "flying"
        category = "Transportation"
        carbon_emission = 200.0
    elif "bus" in message_lower or "train" in message_lower:
        activity = "public transport"
        category = "Transportation"
        carbon_emission = 3.0
    elif "beef" in message_lower or "meat" in message_lower:
        activity = "eating meat"
        category = "Food"
        carbon_emission = 12.0
    elif "vegetarian" in message_lower or "plant-based" in message_lower:
        activity = "plant-based meal"
        category = "Food"
        carbon_emission = 2.0
    elif "electricity" in message_lower or "energy" in message_lower:
        activity = "home energy use"
        category = "Energy"
        carbon_emission = 25.0
    elif "recycling" in message_lower:
        activity = "recycling"
        category = "Waste"
        carbon_emission = 1.0

    # If activity detected, get eco points prediction
    if activity and category and carbon_emission is not None:
        eco_points = ai_service.predict_eco_points(activity, category, carbon_emission)

    # Generate response (can handle general questions or activity-specific advice)
    response = await ai_service.generate_response(message, activity, category, carbon_emission, eco_points)

    return {"response": response}


# -------------------------#
# Train AI Model
# -------------------------#
@router.post("/train", response_model=dict)
def train_ai_model():
    """Train the AI model with synthetic data"""
    try:
        result = ai_service.train_model(500)
        return {
            "message": "AI model trained successfully with 500 examples (80/20 split)",
            "metrics": result
        }
    except Exception as e:
        return {"error": f"Training failed: {str(e)}"}


# -------------------------#
# Predict Eco Points
# -------------------------#
@router.post("/predict", response_model=dict)
async def predict_eco_points(request: dict):
    """Predict eco points for a given activity"""
    try:
        activity = request.get("activity", "general activity")
        category = request.get("category", "Lifestyle")
        carbon_emission = request.get("carbon_emission", 5.0)

        eco_points = ai_service.predict_eco_points(activity, category, carbon_emission)
        advice = await ai_service.generate_response(
            f"I performed {activity} in {category} with {carbon_emission}kg CO2 emissions",
            activity,
            category,
            carbon_emission,
            eco_points,
        )

        return {
            "activity": activity,
            "category": category,
            "carbon_emission": carbon_emission,
            "predicted_eco_points": eco_points,
            "advice": advice
        }
    except Exception as e:
        return {"error": f"Prediction failed: {str(e)}"}


# -------------------------#
# Log Activity with AI
# -------------------------#
@router.post("/log", response_model=dict)
async def add_log_with_ai(request: dict, current_user: models.User = Depends(get_current_user)):
    """Create a log entry with calculated emissions and eco points"""
    try:
        # Calculate carbon emissions using the calculator
        carbon_emission = EmissionsCalculator.calculate_emissions(request)
        
        # Get activity details
        activity = str(request.get("activity", "general activity"))
        category = str(request.get("category", "Lifestyle"))
        
        # Calculate eco points using AI service
        eco_points = ai_service.predict_eco_points(activity, category, carbon_emission)
        
        # Generate advice using AI
        advice = await ai_service.generate_response(
            f"I logged {activity} in {category} with {carbon_emission}kg CO2",
            activity,
            category,
            carbon_emission,
            eco_points
        )

        return {
            "activity": activity,
            "category": category,
            "distance": request.get("distance"),
            "quantity": request.get("quantity"),
            "mode": request.get("mode"),
            "details": request.get("details"),
            "carbon_emission": round(carbon_emission, 3),
            "eco_points": eco_points,
            "advice": advice,
            "original_log": request
        }
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Log processing failed: {str(e)}"
        )


# -------------------------#
# Calculate Eco Points
# -------------------------#
@router.post("/calculate-points", response_model=schemas.CalculatePointsResponse)
async def calculate_eco_points(
    request: schemas.CalculatePointsRequest,
    current_user: models.User = Depends(get_current_user),
):
    """Calculate eco points for given activity parameters"""
    try:
        eco_points = ai_service.predict_eco_points(
            request.activity,
            request.category,
            request.carbon_emission
        )
        
        message = await ai_service.generate_response(
            f"Calculate points for {request.activity}",
            request.activity,
            request.category,
            request.carbon_emission,
            eco_points
        )
        
        return {
            "eco_points": eco_points,
            "prediction_type": "model" if ai_service.is_trained else "fallback",
            "message": message
        }
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error calculating eco points: {str(e)}"
        )
