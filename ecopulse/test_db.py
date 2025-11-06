# test_db_fixed.py
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_database():
    try:
        # Import after path is set
        from app.core.database import engine, get_db
        from app.models.user import User
        
        # Test connection
        with engine.connect() as conn:
            print("✅ Database connection successful!")
        
        # Test if tables exist
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        print(f"📊 Tables found: {tables}")
        
        if 'users' in tables:
            # Test query
            db = next(get_db())
            try:
                user_count = db.query(User).count()
                print(f"👥 Users in database: {user_count}")
                
                # Test if we can access relationships
                if user_count > 0:
                    user = db.query(User).first()
                    print(f"✅ User model works: {user.email}")
                    
            except Exception as e:
                print(f"❌ Query error: {e}")
            finally:
                db.close()
            
        return True
        
    except Exception as e:
        print(f"❌ Database error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_database()