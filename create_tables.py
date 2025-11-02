from app.database import engine
from app import models

def create_tables():
    print("Creating database tables...")
    models.Base.metadata.create_all(bind=engine)
    print("Tables created successfully!")

if __name__ == "__main__":
    create_tables()
