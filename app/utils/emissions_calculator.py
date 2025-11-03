from typing import Dict, Any, Optional

class EmissionsCalculator:
    TRANSPORT_FACTORS = {
        "car": 0.21,           # kg CO2 per km
        "electric_car": 0.05,
        "bus": 0.05,
        "train": 0.04,
        "plane": 0.11,
        "bike": 0,
        "walk": 0
    }
    
    FOOD_FACTORS = {
        "beef": 27.0,          # kg CO2 per kg
        "pork": 12.1,
        "chicken": 6.9,
        "fish": 6.1,
        "vegetarian": 2.0,
        "vegan": 1.5
    }
    
    ENERGY_FACTORS = {
        "electricity": 0.233,  # kg CO2 per kWh
        "natural_gas": 0.198,
        "solar": 0
    }

    @staticmethod
    def calculate_emissions(log_data: Dict[str, Any]) -> float:
        category = log_data.get("category", "").lower()
        activity = log_data.get("activity", "").lower()
        distance = float(log_data.get("distance", 0))
        quantity = float(log_data.get("quantity", 0))
        mode = log_data.get("mode", "").lower()

        if category == "transportation":
            factor = EmissionsCalculator.TRANSPORT_FACTORS.get(mode, EmissionsCalculator.TRANSPORT_FACTORS["car"])
            return distance * factor if distance else 15.0  # default car trip

        elif category == "food":
            if "beef" in activity:
                return quantity * EmissionsCalculator.FOOD_FACTORS["beef"] if quantity else 27.0
            elif "vegetarian" in activity:
                return quantity * EmissionsCalculator.FOOD_FACTORS["vegetarian"] if quantity else 2.0
            return quantity * 5.0 if quantity else 5.0  # default meal

        elif category == "energy":
            if quantity:
                factor = EmissionsCalculator.ENERGY_FACTORS.get(mode, EmissionsCalculator.ENERGY_FACTORS["electricity"])
                return quantity * factor
            return 25.0  # default daily energy use

        elif category == "waste":
            return 1.0  # base waste emission

        return 5.0  # default emission
