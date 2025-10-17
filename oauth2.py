import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

# Import database and models to fetch the user from the DB
from database import get_db
from models import User

# Load environment variables from .env file
load_dotenv()

# --- Configuration ---
# This scheme tells FastAPI where to go to get the token (the /login endpoint)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

# --- Token Creation ---
def create_access_token(data: dict):
    """
    Creates a new JWT access token.
    """
    to_encode = data.copy()
    
    # Set the expiration time for the token
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    
    # Encode the token with the secret key and algorithm
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return encoded_jwt

# --- Token Verification ---
def verify_access_token(token: str, credentials_exception):
    """
    Verifies the access token. Returns the token's payload if valid.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        
        if username is None:
            raise credentials_exception
        
        # You could add more validation here if needed, creating a TokenData schema
        return username
    except JWTError:
        raise credentials_exception

# --- Get Current User ---
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    A dependency that can be used in path operations to get the current user.
    It verifies the token and fetches the user from the database.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # Verify the token to get the username
    username = verify_access_token(token, credentials_exception)
    
    # Get the user's data from the database
    user = db.query(User).filter(User.username == username).first()
    
    if user is None:
        raise credentials_exception
        
    return user

# --- Refresh Token Creation ---
def create_refresh_token(data: dict):
    """
    Creates a long-lived refresh token (default: 7 days).
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=7)
    to_encode.update({"exp": expire})
    refresh_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return refresh_jwt