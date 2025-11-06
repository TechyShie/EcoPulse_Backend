import os
import httpx
import re
import json
from fastapi import HTTPException
from ..core.config import settings

async def get_ai_response(message: str) -> str:
    """For general eco-chat"""
    print(f"🔍 AI Service Debug: Received message: '{message}'")
    print(f"🔍 AI Service Debug: OPENROUTER_API_KEY exists: {bool(settings.OPENROUTER_API_KEY)}")
    
    if settings.OPENROUTER_API_KEY:
        print("🔍 AI Service Debug: Attempting OpenRouter API call...")
        try:
            response = await call_openrouter_chat(message)
            print(f"🔍 AI Service Debug: OpenRouter response: {response}")
            return response
        except Exception as e:
            print(f"🔍 AI Service Debug: OpenRouter API error: {e}")
    else:
        print("🔍 AI Service Debug: No OPENROUTER_API_KEY found")
    
    # Fallback response
    fallback = get_smart_fallback_response(message)
    print(f"🔍 AI Service Debug: Using fallback response: {fallback}")
    return fallback

async def calculate_emission_points(activity: str, category: str, details: str = None) -> dict:
    """
    AI-powered emission and points calculation
    Returns: {"carbon_emission": float, "eco_points": int, "explanation": str}
    """
    print(f"🔍 AI Calculation Debug: activity='{activity}', category='{category}', details='{details}'")
    
    if settings.OPENROUTER_API_KEY:
        try:
            result = await ai_calculate_emission_points(activity, category, details)
            print(f"🔍 AI Calculation Debug: AI result: {result}")
            return result
        except Exception as e:
            print(f"AI calculation error: {e}")
    
    # Fallback calculation
    fallback_result = get_fallback_calculation(activity, category, details)
    print(f"🔍 AI Calculation Debug: Fallback result: {fallback_result}")
    return fallback_result

async def ai_calculate_emission_points(activity: str, category: str, details: str) -> dict:
    """AI-powered calculation using OpenRouter + DeepSeek"""
    
    prompt = f"""
    As an environmental scientist, calculate the carbon emissions saved and eco points for this activity.
    
    ACTIVITY: {activity}
    CATEGORY: {category}
    DETAILS: {details or "No additional details"}
    
    Calculate:
    1. CARBON EMISSIONS SAVED (in kg CO2): Estimate based on typical emissions for this type of activity
    2. ECO POINTS: Award points based on environmental impact (1 point per 0.1 kg CO2 saved)
    
    IMPORTANT: Return ONLY valid JSON in this exact format:
    {{
        "carbon_emission": 1.25,
        "eco_points": 12,
        "explanation": "Brief explanation of the calculation"
    }}
    
    Guidelines:
    - Transportation (cycling, walking, public transit): 0.5-5 kg CO2 saved per trip
    - Energy conservation: 0.1-3 kg CO2 saved per action  
    - Waste reduction: 0.1-2 kg CO2 saved per action
    - Sustainable food: 0.5-4 kg CO2 saved per meal
    - Eco-shopping: 0.1-2 kg CO2 saved per purchase
    
    Be realistic and conservative. Round to 2 decimal places.
    """
    
    # OpenRouter API endpoint with corrected format
    API_URL = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
        "HTTP-Referer": "http://localhost:8080",
        "X-Title": "EcoPulse",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "deepseek/deepseek-r1-0528:free",  # Corrected model name
        "messages": [
            {
                "role": "system",
                "content": "You are an environmental scientist specializing in carbon emissions calculation. Always respond with valid JSON in the exact format specified. Do not include any additional text outside the JSON."
            },
            {
                "role": "user", 
                "content": prompt
            }
        ],
        "max_tokens": 500,
        "temperature": 0.3
    }
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        print(f"🔄 Calling OpenRouter for emission calculation...")
        response = await client.post(API_URL, headers=headers, json=payload)
        
        print(f"📊 Response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"OpenRouter Response: {result}")
            
            if "choices" in result and len(result["choices"]) > 0:
                ai_text = result["choices"][0]["message"]["content"]
                print(f"AI Response content: {ai_text}")
                return parse_ai_calculation(ai_text)
            else:
                print(f"Unexpected response format: {result}")
        
        # If API call fails, use fallback
        print(f"API call failed with status {response.status_code}: {response.text}")
        return get_fallback_calculation(activity, category, details)

def parse_ai_calculation(ai_text: str) -> dict:
    """Parse AI response to extract calculation data"""
    try:
        # Clean the response text
        cleaned_text = ai_text.strip()
        print(f"Parsing AI text: {cleaned_text}")
        
        # Parse JSON directly
        data = json.loads(cleaned_text)
        
        # Validate required fields
        if all(k in data for k in ['carbon_emission', 'eco_points']):
            return {
                "carbon_emission": float(data["carbon_emission"]),
                "eco_points": int(data["eco_points"]),
                "explanation": data.get("explanation", "AI-calculated based on activity details")
            }
    except Exception as e:
        print(f"Error parsing AI response: {e}")
        # Try regex fallback for malformed JSON
        try:
            json_match = re.search(r'\{[^{}]*\}', cleaned_text)
            if json_match:
                json_str = json_match.group()
                print(f"Found JSON with regex: {json_str}")
                data = json.loads(json_str)
                if all(k in data for k in ['carbon_emission', 'eco_points']):
                    return {
                        "carbon_emission": float(data["carbon_emission"]),
                        "eco_points": int(data["eco_points"]),
                        "explanation": data.get("explanation", "AI-calculated based on activity details")
                    }
        except Exception as e2:
            print(f"Regex parsing also failed: {e2}")
    
    # Fallback if parsing fails
    print("JSON parsing failed, using fallback")
    return get_fallback_calculation("general", "activity", "")

def get_fallback_calculation(activity: str, category: str, details: str) -> dict:
    """Fallback calculation based on category"""
    
    category_base = {
        "transportation": {"emission": 2.5, "points": 25},
        "energy": {"emission": 1.2, "points": 12},
        "waste": {"emission": 0.8, "points": 8},
        "food": {"emission": 1.8, "points": 18},
        "shopping": {"emission": 1.0, "points": 10}
    }
    
    base = category_base.get(category.lower(), {"emission": 1.0, "points": 10})
    
    # Adjust based on activity description
    activity_lower = activity.lower()
    if any(word in activity_lower for word in ['long', 'big', 'major', 'significant', 'extended']):
        base["emission"] *= 1.5
        base["points"] = int(base["emission"] * 10)
    elif any(word in activity_lower for word in ['small', 'quick', 'minor', 'brief']):
        base["emission"] *= 0.5
        base["points"] = int(base["emission"] * 10)
    
    return {
        "carbon_emission": round(base["emission"], 2),
        "eco_points": base["points"],
        "explanation": f"Calculated based on {category} activity: {activity}"
    }

async def call_openrouter_chat(message: str) -> str:
    """Use OpenRouter API for chat with corrected format"""
    
    API_URL = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
        "HTTP-Referer": "http://localhost:8080",
        "X-Title": "EcoPulse",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "deepseek/deepseek-r1-0528:free",  # Corrected model name
        "messages": [
            {
                "role": "system",
                "content": """You are EcoAssistant, an AI focused on environmental sustainability and eco-friendly living. 
                Provide practical, actionable advice about:
                - Reducing carbon footprint
                - Sustainable living practices
                - Eco-friendly products and alternatives
                - Energy conservation
                - Waste reduction and recycling
                - Green transportation
                - Environmental impact tracking
                
                Keep responses concise (2-3 paragraphs max), practical, and encouraging.
                Include specific examples when possible."""
            },
            {
                "role": "user",
                "content": message
            }
        ],
        "max_tokens": 500,
        "temperature": 0.7
    }
    
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            print(f"🔄 Calling OpenRouter API...")
            response = await client.post(API_URL, headers=headers, json=payload)
            
            print(f"📊 Response status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"📊 Raw API response: {result}")
                
                if "choices" in result and len(result["choices"]) > 0:
                    ai_response = result["choices"][0]["message"]["content"].strip()
                    if ai_response:
                        print(f"✅ OpenRouter API success: {ai_response}")
                        return ai_response
                
                return "I received your message but couldn't generate a response. Please try again."
            
            else:
                print(f"❌ OpenRouter API error: {response.status_code} - {response.text}")
                return get_smart_fallback_response(message)
                
    except httpx.TimeoutException:
        print("❌ OpenRouter API timeout")
        return get_smart_fallback_response(message)
    except Exception as e:
        print(f"❌ OpenRouter API connection error: {e}")
        return get_smart_fallback_response(message)

def get_smart_fallback_response(message: str) -> str:
    """Provide intelligent fallback responses for common eco-questions"""
    message_lower = message.lower()
    
    # Energy conservation questions
    if any(word in message_lower for word in ['energy', 'conserve', 'save power', 'electricity', 'reduce energy']):
        return """Here are practical ways to conserve energy at home:

🏠 **Home Energy Conservation:**
• Switch to LED bulbs - use 75% less energy than incandescent
• Unplug electronics when not in use (phantom energy drain)
• Use smart power strips to cut power to idle devices
• Install a programmable thermostat
• Seal windows and doors to prevent drafts
• Use natural light during daytime

💡 **Quick Wins:**
• Wash clothes in cold water
• Air dry clothes instead of using dryer
• Lower water heater temperature to 120°F (49°C)
• Use ceiling fans instead of AC when possible
• Cook with lids on pots to reduce energy use

These changes can reduce your energy bill by 20-30% while helping the environment!"""

    # Carbon footprint questions
    elif any(word in message_lower for word in ['carbon', 'emission', 'footprint', 'co2']):
        return """To reduce your carbon footprint:

🚗 **Transportation:**
• Use public transit, bike, or walk instead of driving
• Carpool with colleagues or neighbors
• Maintain proper tire pressure for better fuel efficiency
• Consider an electric or hybrid vehicle for your next car

🏠 **Home & Energy:**
• Switch to renewable energy if available
• Improve home insulation
• Use energy-efficient appliances (Energy Star rated)
• Install solar panels if feasible

🍽️ **Food & Consumption:**
• Reduce meat consumption, especially beef
• Buy local and seasonal produce
• Minimize food waste through meal planning
• Choose products with minimal packaging

Small consistent changes make a big difference over time!"""

    # Plastic waste questions
    elif any(word in message_lower for word in ['plastic', 'waste', 'recycling', 'zero waste']):
        return """Reduce plastic waste effectively:

🛍️ **Shopping Habits:**
• Carry reusable bags, bottles, and containers
• Choose products with minimal or no plastic packaging
• Shop at bulk stores with your own containers
• Avoid single-use plastics (straws, utensils, cups)

🏠 **Home Solutions:**
• Use glass or stainless steel food storage
• Choose bar soap instead of liquid in plastic bottles
• Make your own cleaning products
• Properly recycle plastics according to local guidelines

🌱 **Lifestyle Changes:**
• Support companies using sustainable packaging
• Bring your own coffee cup to cafes
• Use reusable produce bags
• Choose cardboard packaging over plastic when possible

Every piece of plastic avoided helps our oceans and landfills!"""

    # Default response for other questions
    else:
        return """I'd love to help with your eco-friendly questions! Here are some topics I can assist with:

• Reducing carbon footprint and emissions
• Sustainable shopping and consumption
• Energy and water conservation tips  
• Waste reduction and recycling guidance
• Eco-friendly transportation options
• Green home improvements
• Environmental impact tracking
• Sustainable food choices

Please ask me about any of these topics, or let me know what specific environmental challenge you're facing!

💚 Remember: Small changes collectively make a big impact on our planet!"""