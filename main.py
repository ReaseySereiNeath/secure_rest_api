# main.py
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from database import get_db 
from models import User, Item
from schemas import UserCreate, UserOut, ItemCreate, ItemOut
from auth import hash_password, verify_password
from oauth2 import create_access_token, get_current_user, create_refresh_token, SECRET_KEY, ALGORITHM
from jose import JWTError, jwt

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
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    # Verify password
    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    # Create JWT token by calling the function from oauth2.py
    access_token = create_access_token(data={"sub": user.username})
    refresh_token = create_refresh_token(data={"sub": user.username})

    # Return token
    return {"access_token": access_token, "refresh_token": refresh_token,"token_type": "bearer"}


@app.post("/refresh")
def refresh_token(token: str):
    """
    Refresh the access token using a valid refresh token.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid refresh token")

        # Create a new access token (short-lived)
        new_access_token = create_access_token(data={"sub": username})
        return {"access_token": new_access_token, "token_type": "bearer"}

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")
    

@app.get("/me")
def read_current_user(current_user: User = Depends(get_current_user)):
    return {"logged_in_as": current_user.username, "email": current_user.email}


# ---------- Protected CRUD: /items ----------

@app.post("/items", response_model=ItemOut)
def create_item(
    item: ItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new item for the logged-in user.
    """
    new_item = Item(
        title=item.title,
        description=item.description,
        owner_id=current_user.id
    )
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return new_item

@app.get("/items", response_model=list[ItemOut])
def get_items(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all items owned by the logged-in user.
    """
    return db.query(Item).filter(Item.owner_id == current_user.id).all()


@app.put("/items/{item_id}", response_model=ItemOut)
def update_item(
    item_id: int,
    updated_item: ItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update an item (ownership check).
    """
    
    item = db.query(Item).filter(Item.id == item_id, Item.owner_id == current_user.id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found or not authorized")
    
    item.title = updated_item.title
    item.description = updated_item.description
    db.commit()
    db.refresh(item)
    return item


@app.delete("/items/{item_id}")
def delete_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete an item (ownership check).
    """
    item = db.query(Item).filter(Item.id == item_id, Item.owner_id == current_user.id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found or not authorized")
    
    db.delete(item)
    db.commit()
    return {"message": f"Item {item_id} deleted successfully"}

