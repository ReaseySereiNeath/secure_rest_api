from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# SQLite database URL (local file)
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

# Create the database engine
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# Create a SessionLocal class for database sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for all ORM models
Base = declarative_base()

# Dependency for FastAPI routes to access DB
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()