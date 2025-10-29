import os
from datetime import timedelta
from dotenv import load_dotenv

# ENV selector: 'dev' or 'prod' (default: dev)
ENV = os.getenv("ENV", "dev")
load_dotenv(f".env.{ENV}", override=True)

# Basic settings
DEBUG = os.getenv("DEBUG", "False").lower() == "true"
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-me")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "15"))
REFRESH_TOKEN_EXPIRE_MINUTES = int(os.getenv("REFRESH_TOKEN_EXPIRE_MINUTES", "43200"))  # 30 days

# Rate limit (used by rate_limit.py if desired)
DEFAULT_RATE_LIMIT = os.getenv("DEFAULT_RATE_LIMIT", "5/minute")
LOGIN_RATE_LIMIT = os.getenv("LOGIN_RATE_LIMIT", "5/minute")
ITEMS_RATE_LIMIT = os.getenv("ITEMS_RATE_LIMIT", "10/minute")

# Migration control
RUN_MIGRATIONS_ON_STARTUP = os.getenv("RUN_MIGRATIONS_ON_STARTUP", "false").lower() == "true"
