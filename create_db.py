# create_db.py
from database import Base, engine
from models import User, Item

print("Creating database tables...")
Base.metadata.create_all(bind=engine)
print("Database initialized successfully!")
