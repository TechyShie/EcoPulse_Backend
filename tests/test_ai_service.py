import pytest
from app.services.ai_service import AIService
import pandas as pd
import numpy as np
from unittest.mock import patch

@pytest.fixture
def ai_service():
    service = AIService()
    return service

def test_generate_training_data(ai_service):
    df = ai_service.generate_training_data(n_samples=10)
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 10
    assert all(col in df.columns for col in ['activity', 'category', 'carbon_emission', 'eco_points'])

def test_train_model(ai_service):
    result = ai_service.train_model(n_samples=100)
    assert isinstance(result, dict)
    assert 'mse' in result
    assert 'r2_score' in result
    assert ai_service.is_trained
    assert ai_service.model is not None

def test_predict_eco_points(ai_service):
    # Test with model not trained (fallback prediction)
    points = ai_service.predict_eco_points(
        activity="cycling to work",
        category="Transportation",
        carbon_emission=0.0
    )
    assert isinstance(points, float)
    assert points >= 0

    # Test with different activities
    test_cases = [
        {
            "activity": "driving car",
            "category": "Transportation",
            "carbon_emission": 15.0,
            "expected_min": 0,
        },
        {
            "activity": "vegetarian meal",
            "category": "Food",
            "carbon_emission": 2.0,
            "expected_min": 50,
        },
        {
            "activity": "recycling",
            "category": "Waste",
            "carbon_emission": 1.0,
            "expected_min": 70,
        }
    ]

    for case in test_cases:
        points = ai_service.predict_eco_points(
            activity=case["activity"],
            category=case["category"],
            carbon_emission=case["carbon_emission"]
        )
        assert isinstance(points, float)
        assert points >= case["expected_min"]

@pytest.mark.asyncio
async def test_generate_response(ai_service):
    response = await ai_service.generate_response(
        message="How can I reduce my carbon footprint?",
        activity="cycling",
        category="Transportation",
        carbon_emission=0.0,
        eco_points=100.0
    )
    assert isinstance(response, str)
    assert len(response) > 0

def test_predict_eco_points_fallback(ai_service):
    points = ai_service.predict_eco_points(
        activity="cycling to work",
        category="Transportation",
        carbon_emission=0.0
    )
    assert isinstance(points, float)
    assert points >= 0
    assert points <= 120  # Base points (100) + max category bonus (20)

@patch('openai.ChatCompletion.create')
def test_fallback_responses(mock_openai, ai_service):
    # Test each category has valid fallback responses
    for category in ["Transportation", "Food", "Energy", "Waste"]:
        response = ai_service._generate_fallback_response(category)
        assert isinstance(response, str)
        assert len(response) > 0
