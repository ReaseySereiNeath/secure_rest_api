# main.py
import logging
from fastapi import FastAPI, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import text

from database import get_db 
from models import User, Item
from schemas import UserCreate, UserOut, ItemCreate, ItemOut
from auth import hash_password, verify_password
from oauth2 import create_access_token, get_current_user, create_refresh_token, SECRET_KEY, ALGORITHM
from jose import JWTError, jwt
from middlewares.logging import LoggingMiddleware
from middlewares.error_handler import ExceptionLoggingMiddleware
from middlewares.rate_limit import register_rate_limiter, limiter
from fastapi.openapi.utils import get_openapi
# Config-driven limits and migration flag
from config import LOGIN_RATE_LIMIT, ITEMS_RATE_LIMIT, RUN_MIGRATIONS_ON_STARTUP
import os
from alembic.config import Config
from alembic import command

logger = logging.getLogger(__name__)

app = FastAPI()
register_rate_limiter(app)
app.add_middleware(ExceptionLoggingMiddleware)
app.add_middleware(LoggingMiddleware)


@app.get("/")
def home():
    return {"message": "Welcome to Secure REST API"}


@app.get("/users", response_model=list[UserOut])
def read_users(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    users = db.query(User).all()
    return users


@app.post("/register", response_model=UserOut)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    existing_username = db.query(User).filter(User.username == user.username).first()
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered",
        )

    existing_email = db.query(User).filter(User.email == user.email).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
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
@limiter.limit(LOGIN_RATE_LIMIT)
def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    # Find user by username
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
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


@app.get("/admin/users")
def get_all_users(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Admin-only route: list all users.
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )

    users = db.query(User).all()
    return [{"id": u.id, "username": u.username, "email": u.email, "is_admin": u.is_admin} for u in users]


@app.get("/crash-test")
def crash_test():
    raise RuntimeError("This is a simulated crash for testing the error logger.")


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
@limiter.limit(ITEMS_RATE_LIMIT)
def get_items(
    request: Request,
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


# Health check route — no limit
@app.get("/health")
@limiter.exempt
def health_check(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {"status": "healthy"}
    except Exception:
        raise HTTPException(status_code=503, detail="Database unavailable")

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title="Secure REST API",
        version="1.0.0",
        description="A secure REST API with JWT authentication, logging, error handling, and rate limiting.",
        routes=app.routes,
    )
    
    # Add global JWT (Bearer) security definition
    openapi_schema["components"] = openapi_schema.get("components", {})
    openapi_schema["components"]["securitySchemes"] = {
        "OAuth2PasswordBearer": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }
    openapi_schema["security"] = [{"OAuth2PasswordBearer": []}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

def run_migrations_on_startup():
    """
    Automatically apply Alembic migrations at startup.
    This keeps the DB schema in sync with your SQLAlchemy models.
    """
    print("Running Alembic migrations on startup...")
    alembic_cfg = Config(os.path.join(os.path.dirname(__file__), "alembic.ini"))
    alembic_cfg.set_main_option("script_location", "alembic")
    command.upgrade(alembic_cfg, "head")
    print("Database is up-to-date.")

@app.on_event("startup")
def startup_event():
    if RUN_MIGRATIONS_ON_STARTUP:
        try:
            run_migrations_on_startup()
        except Exception:
            logger.exception("Alembic migrations failed during startup")
            raise
