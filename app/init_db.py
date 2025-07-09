# init_db.py
from app.database import Base, engine
from app import models  # Ensure models are imported

Base.metadata.create_all(bind=engine)
print("✅ Tables created successfully in SQLite.")