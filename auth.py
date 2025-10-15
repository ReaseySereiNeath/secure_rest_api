# auth.py
from passlib.context import CryptContext

# Create a bcrypt hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str):
    # bcrypt only supports up to 72 bytes; truncate safely
    return pwd_context.hash(password[:72])

def verify_password(plain_password: str, hashed_password: str):
    """Verify a password against its hashed value."""
    return pwd_context.verify(plain_password, hashed_password)