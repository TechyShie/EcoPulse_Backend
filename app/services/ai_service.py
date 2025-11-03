import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import mean_squared_error, r2_score
import joblib
import os
from typing import Optional, Dict, Any
import random
import logging
from app.core.settings import settings
import asyncio

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    import openai
except ImportError:
    logger.warning("OpenAI package not installed. Using fallback responses.")
    openai = None


class AIService:
    def __init__(self):
        self.model_path = "app/models/ai_model.pkl"
        self.encoder_path = "app/models/label_encoder.pkl"
        self.scaler_path = "app/models/scaler.pkl"
        self.model = None
        self.encoder = None
        self.scaler = None
        self.is_trained = False
        self.fallback_responses = {
            "Transportation": [
                "Consider using public transport or cycling for shorter trips.",
                "Carpooling can significantly reduce your carbon footprint.",
                "Regular vehicle maintenance helps optimize fuel efficiency.",
            ],
            "Food": [
                "Try incorporating more plant-based meals into your diet.",
                "Buy local and seasonal produce when possible.",
                "Reduce food waste by planning meals ahead.",
            ],
            "Energy": [
                "Use energy-efficient appliances and LED lighting.",
                "Consider natural lighting and ventilation when possible.",
                "Unplug devices when not in use to avoid phantom energy usage.",
            ],
            "Waste": [
                "Remember to reduce, reuse, and recycle.",
                "Composting organic waste helps reduce methane emissions.",
                "Choose products with minimal packaging.",
            ],
        }

    def generate_training_data(self, n_samples: int = 500) -> pd.DataFrame:
        """Generate synthetic training data for eco-points prediction"""
        np.random.seed(42)

        # Define categories and their typical carbon emissions ranges
        categories = {
            "Transportation": {"min": 0.1, "max": 50.0, "avg": 15.0},
            "Food": {"min": 0.5, "max": 30.0, "avg": 8.0},
            "Energy": {"min": 1.0, "max": 100.0, "avg": 25.0},
            "Waste": {"min": 0.1, "max": 20.0, "avg": 5.0},
            "Shopping": {"min": 0.5, "max": 40.0, "avg": 12.0},
            "Lifestyle": {"min": 0.2, "max": 25.0, "avg": 7.0},
        }

        data = []

        for _ in range(n_samples):
            category = np.random.choice(list(categories.keys()))
            cat_info = categories[category]

            # Generate carbon emission based on category
            carbon_emission = np.random.normal(cat_info["avg"], cat_info["avg"] * 0.3)
            carbon_emission = max(cat_info["min"], min(cat_info["max"], carbon_emission))

            # Generate activity name based on category
            activity_templates = {
                "Transportation": [
                    "Driving to work",
                    "Flight to NYC",
                    "Bus commute",
                    "Cycling",
                    "Walking",
                    "Electric car trip",
                ],
                "Food": [
                    "Beef dinner",
                    "Vegetarian meal",
                    "Fast food",
                    "Local produce",
                    "Imported fruit",
                    "Plant-based diet",
                ],
                "Energy": [
                    "Home electricity",
                    "Heating bill",
                    "Solar panels",
                    "LED bulbs",
                    "Appliance usage",
                    "Renewable energy",
                ],
                "Waste": [
                    "Plastic bottles",
                    "Paper recycling",
                    "Composting",
                    "Landfill waste",
                    "E-waste",
                    "Textile recycling",
                ],
                "Shopping": [
                    "New clothes",
                    "Electronics",
                    "Local products",
                    "Second-hand items",
                    "Bulk buying",
                    "Minimalist purchase",
                ],
                "Lifestyle": [
                    "Water usage",
                    "Air conditioning",
                    "Home office",
                    "Gardening",
                    "Pet care",
                    "Home maintenance",
                ],
            }

            activity = np.random.choice(activity_templates[category])

            # Calculate eco points (higher points for lower emissions, with category multipliers)
            category_multipliers = {
                "Transportation": 1.2,
                "Food": 1.0,
                "Energy": 1.3,
                "Waste": 0.8,
                "Shopping": 0.9,
                "Lifestyle": 0.7,
            }

            # Eco points formula: base points minus emission penalty, plus category bonus
            base_points = 100
            emission_penalty = carbon_emission * 2
            category_bonus = category_multipliers[category] * 10
            eco_points = max(0, base_points - emission_penalty + category_bonus)

            data.append(
                {
                    "activity": activity,
                    "category": category,
                    "carbon_emission": round(carbon_emission, 2),
                    "eco_points": round(eco_points, 1),
                }
            )

        return pd.DataFrame(data)

    def train_model(self, n_samples: int = 500):
        """Train the AI model using 80/20 split"""
        # Generate training data
        df = self.generate_training_data(n_samples)

        # Prepare features
        self.encoder = LabelEncoder()
        df["category_encoded"] = self.encoder.fit_transform(df["category"])

        # Create activity type features (simplified NLP)
        df["activity_length"] = df["activity"].str.len()
        df["has_sustainable"] = df["activity"].str.contains(
            "solar|electric|cycling|walking|recycling|compost|local|second-hand|plant-based",
            case=False,
        ).astype(int)

        # Features for training
        features = ["carbon_emission", "category_encoded", "activity_length", "has_sustainable"]
        X = df[features]
        y = df["eco_points"]

        # Split data 80/20
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        # Scale features
        self.scaler = StandardScaler()
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)

        # Train model
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.model.fit(X_train_scaled, y_train)

        # Evaluate model
        y_pred = self.model.predict(X_test_scaled)
        mse = mean_squared_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)

        print(f"Model trained successfully!")
        print(f"MSE: {mse:.2f}")
        print(f"R² Score: {r2:.2f}")

        # Save model and preprocessing objects
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        joblib.dump(self.model, self.model_path)
        joblib.dump(self.encoder, self.encoder_path)
        joblib.dump(self.scaler, self.scaler_path)

        self.is_trained = True
        return {"mse": mse, "r2_score": r2}

    def load_model(self):
        """Load trained model if it exists"""
        if os.path.exists(self.model_path):
            self.model = joblib.load(self.model_path)
            self.encoder = joblib.load(self.encoder_path)
            self.scaler = joblib.load(self.scaler_path)
            self.is_trained = True
            return True
        return False

    def predict_eco_points(self, activity: str, category: str, carbon_emission: float) -> float:
        """Predict eco points for a given activity"""
        if not self.is_trained and not self.load_model():
            # Fallback to simple calculation if model not trained
            return self._fallback_prediction(activity, category, carbon_emission)

        # Prepare input features
        category_encoded = self.encoder.transform([category])[0]
        activity_length = len(activity)
        has_sustainable = 1 if "solar" in activity.lower() or "electric" in activity.lower() or "cycling" in activity.lower() or "walking" in activity.lower() or "recycling" in activity.lower() or "compost" in activity.lower() or "local" in activity.lower() or "second-hand" in activity.lower() or "plant-based" in activity.lower() else 0

        features = np.array([[carbon_emission, category_encoded, activity_length, has_sustainable]])
        features_scaled = self.scaler.transform(features)

        prediction = self.model.predict(features_scaled)[0]
        return round(max(0, prediction), 1)

    def _fallback_prediction(self, activity: str, category: str, carbon_emission: float) -> float:
        """Fallback prediction when model is not available"""
        base_points = 100
        emission_penalty = carbon_emission * 2

        category_multipliers = {
            "Transportation": 1.2,
            "Food": 1.0,
            "Energy": 1.3,
            "Waste": 0.8,
            "Shopping": 0.9,
            "Lifestyle": 0.7,
        }

        category_bonus = category_multipliers.get(category, 1.0) * 10
        sustainable_bonus = 10 if any(word in activity.lower() for word in ["solar", "electric", "cycling", "walking", "recycling", "compost", "local", "second-hand", "plant-based"]) else 0

        return max(0, base_points - emission_penalty + category_bonus + sustainable_bonus)

    async def generate_response(self, message: str, activity: str = None, category: str = None, 
                              carbon_emission: float = None, eco_points: float = None) -> str:
        """Generate eco-related responses using OpenAI GPT for natural, conversational responses"""
        if not openai:
            return self._generate_fallback_response(category)

        try:
            if not settings.OPENAI_API_KEY:
                logger.warning("OpenAI API key not configured")
                return self._generate_fallback_response(category)
                
            openai.api_key = settings.OPENAI_API_KEY

            # Build context based on available information
            context = ""
            if activity and category and carbon_emission is not None and eco_points is not None:
                context = f"The user performed an activity: '{activity}' in category '{category}' with estimated {carbon_emission}kg CO2 emissions. They earned {eco_points} eco-points for this activity."

            prompt = f"""
            You are an eco-friendly AI assistant helping users with environmental questions and activities.
            {context}

            User's message: "{message}"

            Provide a friendly, conversational response that:
            1. Addresses the user's question or comment about environmental topics
            2. If activity details are provided, acknowledges their activity and eco-points earned
            3. Gives helpful, accurate information about environmental impact, sustainability, or eco-friendly practices
            4. Suggests specific, actionable steps when relevant
            5. Encourages positive environmental behavior
            6. Keep the response natural and engaging, like a helpful friend

            Response should be 2-4 sentences long and end on a positive, motivating note.
            Only respond to eco-related topics; if the question is not eco-related, politely redirect to environmental topics.
            """

            response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a helpful eco-assistant providing information and advice on environmental topics."},
                        {"role": "user", "content": prompt},
                    ],
                    max_tokens=200,
                    temperature=0.7,
                )
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            logger.error(f"Error generating AI response: {e}")
            return self._generate_fallback_response(category)

    def _generate_fallback_response(self, category: Optional[str] = None) -> str:
        if category and category in self.fallback_responses:
            return random.choice(self.fallback_responses[category])
        return random.choice([resp for responses in self.fallback_responses.values() for resp in responses])


# Global AI service instance
ai_service = AIService()
