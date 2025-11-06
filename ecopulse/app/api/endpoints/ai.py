from fastapi import APIRouter, Depends, Body
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from ...services.ai_service import get_ai_response, calculate_emission_points
from ...api.dependencies import get_current_user

router = APIRouter()

# Chat request/response models
class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str

# Calculate points request/response models  
class CalculatePointsRequest(BaseModel):
    activity: str
    category: str
    details: Optional[str] = None
    date: Optional[datetime] = None

class CalculatePointsResponse(BaseModel):
    carbon_emission: float
    eco_points: int
    explanation: Optional[str] = None

@router.post("/chat", response_model=ChatResponse)
async def chat_with_ai(
    chat_request: ChatRequest = Body(
        ...,
        example={
            "message": "How can I reduce my carbon footprint?"
        },
        description="Chat with eco AI assistant"
    ),
    current_user = Depends(get_current_user)
):
    """
    Chat with the EcoPulse AI assistant about sustainability topics
    
    Ask questions about:
    - Reducing carbon footprint
    - Sustainable living practices  
    - Eco-friendly products
    - Energy conservation
    - Waste reduction
    """
    response = await get_ai_response(chat_request.message)
    return ChatResponse(response=response)

@router.post("/calculate-points", response_model=CalculatePointsResponse)
async def calculate_points(
    activity: str = Body(..., example="Cycled to work instead of driving"),
    category: str = Body(..., example="transportation"),
    details: Optional[str] = Body(None, example="10km commute, avoided car trip"),
    date: Optional[datetime] = Body(None, example="2024-01-15T10:30:00Z"),
    current_user = Depends(get_current_user)
):
    """
    AI-powered calculation of carbon emissions and eco points
    
    **CRITICAL: This endpoint is required for frontend log creation**
    
    **Process:**
    1. Frontend sends activity details
    2. AI calculates carbon emissions (kg CO2) and eco points
    3. Returns values that frontend uses to create log
    
    **Supported Categories:**
    - `transportation` (cycling, walking, public transit, electric vehicles)
    - `energy` (LED lights, reduced electricity, solar power)
    - `waste` (recycling, composting, reducing plastic)
    - `food` (vegetarian meals, local produce, reducing waste)
    - `shopping` (eco-products, minimal packaging, second-hand)
    
    **Example Request:**
    ```json
    {
      "activity": "Cycled to work",
      "category": "transportation", 
      "details": "10km commute instead of driving",
      "date": "2024-01-15T10:30:00Z"
    }
    ```
    
    **Example Response:**
    ```json
    {
      "carbon_emission": 2.5,
      "eco_points": 25,
      "explanation": "Cycling 10km saves approximately 2.5kg CO2 compared to driving"
    }
    ```
    """
    result = await calculate_emission_points(
        activity=activity,
        category=category,
        details=details
    )
    
    return CalculatePointsResponse(
        carbon_emission=result["carbon_emission"],
        eco_points=result["eco_points"],
        explanation=result.get("explanation")
    )

# Add test endpoint to verify AI connection
@router.get("/test-connection")
async def test_ai_connection(current_user = Depends(get_current_user)):
    """Test if AI service is properly configured"""
    from ...core.config import settings

    test_result = {
        "api_key_configured": bool(settings.OPENROUTER_API_KEY),
        "service_status": "unknown"
    }

    if settings.OPENROUTER_API_KEY:
        try:
            test_response = await get_ai_response("Hello, are you working?")
            # Check if we got a fallback response (indicates API failure)
            if "I'd love to help with your eco-friendly questions!" in test_response:
                test_result["service_status"] = "api_error_fallback_active"
                test_result["test_response_preview"] = "Using fallback responses due to API issues"
            else:
                test_result["service_status"] = "working"
                test_result["test_response_preview"] = test_response[:100] + "..." if len(test_response) > 100 else test_response
        except Exception as e:
            test_result["service_status"] = f"error: {str(e)}"
    else:
        test_result["service_status"] = "no_api_key"

    return test_result
