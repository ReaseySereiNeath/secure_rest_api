# main.py
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from database import get_db 
from models import User
from schemas import UserCreate, UserOut
from auth import hash_password, verify_password
import oauth2

app = FastAPI()

@app.get("/")
def home():
    return {"message": "Welcome to Secure REST API"}

# Add your /users route here
@app.get("/users")
def read_users(db: Session = Depends(get_db)):
    # Fetch all users from the database
    users = db.query(User).all()
    return users

@app.post("/register", response_model=UserOut)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    # Check if username or email already exists
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Hash the password
    hashed_pw = hash_password(user.password)
    
    # Create a new user object
    new_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_pw
    )

    # Save to the database
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user

@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # Find user by username
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid username or password")

    # Verify password
    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    # Create JWT token by calling the function from oauth2.py
    access_token = oauth2.create_access_token(data={"sub": user.username})

    # Return token
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/me")
def read_current_user(current_user: User = Depends(oauth2.get_current_user)):
    return {"logged_in_as": current_user}