#!/usr/bin/env python3
"""
EcoPulse Data Seeding Script
Run this to populate the database with sample users, logs, and badges
"""
import os
import sys
from datetime import datetime, timedelta
import random

# Add the app directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.core.database import SessionLocal, engine
from app.core.security import get_password_hash
from app.models.user import User
from app.models.log import Log
from app.models.badge import Badge, UserBadge

def seed_database():
    print("🚀 Seeding EcoPulse database with sample data...")
    
    db = SessionLocal()
    
    try:
        # Clear existing data (optional - comment out if you want to keep existing data)
        print("Clearing existing data...")
        db.query(UserBadge).delete()
        db.query(Log).delete()
        db.query(Badge).delete()
        db.query(User).delete()
        db.commit()
        
        # Create sample badges
        print("Creating badges...")
        badges = [
            Badge(
                name="Eco Starter",
                description="Logged your first eco activity",
                icon_url="/badges/eco-starter.png",
                requirement="first_log"
            ),
            Badge(
                name="Carbon Crusader", 
                description="Saved 5kg of CO2 emissions",
                icon_url="/badges/carbon-crusader.png",
                requirement="5000_emissions"
            ),
            Badge(
                name="Green Commuter",
                description="10+ transportation activities",
                icon_url="/badges/green-commuter.png",
                requirement="10_transport_logs"
            ),
            Badge(
                name="Energy Saver",
                description="15+ energy conservation activities", 
                icon_url="/badges/energy-saver.png",
                requirement="15_energy_logs"
            ),
            Badge(
                name="Waste Warrior",
                description="20+ waste reduction activities",
                icon_url="/badges/waste-warrior.png", 
                requirement="20_waste_logs"
            ),
            Badge(
                name="Eco Champion",
                description="Reached 500 eco points",
                icon_url="/badges/eco-champion.png",
                requirement="500_points"
            )
        ]
        
        for badge in badges:
            db.add(badge)
        db.commit()
        print(f"✅ Created {len(badges)} badges")
        
        # Create sample users
        print("Creating sample users...")
        users_data = [
            {
                "email": "emma.green@example.com",
                "full_name": "Emma Green", 
                "password": "password123",
                "bio": "Environmental scientist passionate about sustainable living",
                "avatar_url": "https://example.com/avatars/emma.jpg"
            },
            {
                "email": "alex.eco@example.com", 
                "full_name": "Alex Eco",
                "password": "password123",
                "bio": "Urban cyclist and zero-waste advocate",
                "avatar_url": "https://example.com/avatars/alex.jpg"
            },
            {
                "email": "sarah.earth@example.com",
                "full_name": "Sarah Earth",
                "password": "password123", 
                "bio": "Organic farmer and climate activist",
                "avatar_url": "https://example.com/avatars/sarah.jpg"
            },
            {
                "email": "mike.sustainable@example.com",
                "full_name": "Mike Sustainable",
                "password": "password123",
                "bio": "Renewable energy engineer and EV enthusiast", 
                "avatar_url": "https://example.com/avatars/mike.jpg"
            },
            {
                "email": "lisa.planet@example.com",
                "full_name": "Lisa Planet",
                "password": "password123",
                "bio": "Marine biologist focused on ocean conservation",
                "avatar_url": "https://example.com/avatars/lisa.jpg"
            }
        ]
        
        users = []
        for user_data in users_data:
            user = User(
                email=user_data["email"],
                full_name=user_data["full_name"],
                hashed_password=get_password_hash(user_data["password"]),
                bio=user_data["bio"],
                avatar_url=user_data["avatar_url"],
                eco_score=0,
                total_emissions_saved=0
            )
            db.add(user)
            users.append(user)
        
        db.commit()
        print(f"✅ Created {len(users)} sample users")
        
        # Create sample eco logs for each user
        print("Creating sample eco logs...")
        
        activity_templates = [
            # Transportation activities
            {
                "type": "transportation",
                "templates": [
                    ("Cycled to work", "10km commute instead of driving", 2500),
                    ("Took public transit", "Bus instead of personal car", 1800),
                    ("Walked to store", "2km walk for groceries", 800),
                    ("Carpooled with colleagues", "Shared ride to office", 1200),
                    ("Electric scooter commute", "8km on e-scooter", 600)
                ]
            },
            # Energy activities  
            {
                "type": "energy", 
                "templates": [
                    ("LED bulb installation", "Replaced all bulbs with LEDs", 1500),
                    ("Reduced thermostat", "2°C lower in winter", 800),
                    ("Unplugged electronics", "Power strip turned off", 400),
                    ("Solar panel usage", "6 hours of solar power", 3200),
                    ("Energy-efficient appliance", "New Energy Star fridge", 2000)
                ]
            },
            # Waste activities
            {
                "type": "waste",
                "templates": [
                    ("Composting food waste", "Weekly compost collection", 600),
                    ("Recycling plastics", "Sorted and recycled", 450),
                    ("Reusable shopping bags", "Avoided plastic bags", 200),
                    ("Zero-waste shopping", "Bulk store with containers", 350),
                    ("Repaired instead of replaced", "Fixed electronic device", 800)
                ]
            },
            # Food activities
            {
                "type": "food", 
                "templates": [
                    ("Vegetarian meals", "Plant-based diet for a week", 4200),
                    ("Local produce", "Farmers market shopping", 1500),
                    ("Reduced food waste", "Meal planning and leftovers", 900),
                    ("Home gardening", "Grew own vegetables", 1100),
                    ("Sustainable seafood", "Chose MSC-certified fish", 700)
                ]
            },
            # Shopping activities
            {
                "type": "shopping",
                "templates": [
                    ("Eco-friendly products", "Chose sustainable alternatives", 600),
                    ("Second-hand purchase", "Thrift store find", 400),
                    ("Minimal packaging", "Refillable containers", 300),
                    ("Sustainable fashion", "Ethical clothing brand", 500),
                    ("Repair café visit", "Community item repair", 350)
                ]
            }
        ]
        
        # Create logs for each user with varied activity counts
        user_log_counts = [15, 12, 18, 10, 8]  # Different activity levels
        
        for i, user in enumerate(users):
            user_logs = []
            total_emissions = 0
            total_points = 0
            
            # Create logs for this user
            logs_to_create = user_log_counts[i]
            for j in range(logs_to_create):
                # Pick random activity type and template
                activity_type_data = random.choice(activity_templates)
                template = random.choice(activity_type_data["templates"])
                
                # Add some variation to emissions
                emission_variation = random.uniform(0.8, 1.2)
                emissions_saved = int(template[2] * emission_variation)
                points = emissions_saved // 100  # 1 point per 100g
                
                # Random date in the last 30 days
                days_ago = random.randint(0, 30)
                activity_date = datetime.utcnow() - timedelta(days=days_ago)
                
                log = Log(
                    activity_type=activity_type_data["type"],
                    description=template[1],
                    emissions_saved=emissions_saved,
                    points_earned=points,
                    user_id=user.id,
                    activity_date=activity_date
                )
                user_logs.append(log)
                total_emissions += emissions_saved
                total_points += points
            
            # Add logs to database and update user stats
            for log in user_logs:
                db.add(log)
            
            user.total_emissions_saved = total_emissions
            user.eco_score = total_points
            
            print(f"✅ User {user.full_name}: {len(user_logs)} logs, {total_points} points, {total_emissions}g CO2 saved")
        
        db.commit()
        
        # Award some badges to users
        print("Awarding badges...")
        
        # Award Eco Starter to all users
        eco_starter_badge = db.query(Badge).filter(Badge.name == "Eco Starter").first()
        for user in users:
            user_badge = UserBadge(user_id=user.id, badge_id=eco_starter_badge.id)
            db.add(user_badge)
        
        # Award Carbon Crusader to users with high emissions
        carbon_badge = db.query(Badge).filter(Badge.name == "Carbon Crusader").first()
        for user in users[:3]:  # First 3 users
            user_badge = UserBadge(user_id=user.id, badge_id=carbon_badge.id)
            db.add(user_badge)
        
        # Award Eco Champion to top user
        champion_badge = db.query(Badge).filter(Badge.name == "Eco Champion").first()
        top_user = sorted(users, key=lambda u: u.eco_score, reverse=True)[0]
        user_badge = UserBadge(user_id=top_user.id, badge_id=champion_badge.id)
        db.add(user_badge)
        
        db.commit()
        
        print("🎉 Database seeding completed successfully!")
        print("\n📊 Sample Data Summary:")
        print(f"• {len(users)} users created")
        print(f"• {len(badges)} badges created") 
        print(f"• ~{sum(user_log_counts)} eco logs created")
        print(f"• Leaderboard range: {min(u.eco_score for u in users)} - {max(u.eco_score for u in users)} points")
        print(f"• Emissions saved: {sum(u.total_emissions_saved for u in users):,}g CO2 total")
        
        print("\n👤 Sample Login Credentials:")
        for user in users:
            print(f"• {user.email} / password123")
            
    except Exception as e:
        print(f"❌ Error seeding database: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()