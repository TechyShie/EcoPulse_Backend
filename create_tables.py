from app.database import Base, engine
import app.models as models

print("Creating tables...")
Base.metadata.create_all(bind=engine)
print("Done. Tables created in SQLite DB.")
