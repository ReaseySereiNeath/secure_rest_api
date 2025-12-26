# Project 1: Secure REST API with JWT Authenticatio

**Objective:** Build a secure CRUD API that uses JWT tokens for authentication and authorization.

## 📆 Week 1: Setup & User Authentication

### 🎯 **Goals**

- Learn API fundamentals
- Implement user registration, login, and JWT token issuance

### 🧱 Tasks

- [x]  Install and set up **FastAPI**, **Uvicorn**, **SQLModel** (or SQLite)
- [x]  Create `User` model with `username`, `email`, `hashed_password`
- [x]  Use **bcrypt** for password hashing (`passlib[bcrypt]`)
- [x]  Add `/register` route to create users
- [x]  Add `/login` route to verify credentials and return JWT token
- [x]  Configure JWT creation & verification (using `python-jose` or `fastapi-jwt-auth`)

## 📆 Week 2: Protected CRUD API & Security Enhancements

### 🎯 **Goals**

- Add token-based protection to CRUD routes
- Enforce secure access control and error handling

### 🧱 Tasks

- [x]  Create a new model `Item` (title, description, owner_id)
- [x]  Add `/items` CRUD routes (GET, POST, PUT, DELETE)
- [x]  Add JWT `Depends()` middleware to protect routes
- [x]  Return 401 if JWT invalid/expired
- [x]  Implement token expiry (e.g., 15 min) + refresh endpoint
- [x]  Add role-based access control (optional: `is_admin` field)
- [x]  Add request/response logging

## 📆 Week 3: Advanced API Hardening & DevOps Setup

### 🎯 **Goals**

- Strengthen API reliability, scalability, and observability.
- Prepare the Secure REST API for containerized deployment.
- Add operational monitoring and configuration flexibility.

### 🧱 Tasks

- [x]  Add rate limiting
- [x]  **Add API health check**
- [x]  **Add structured JSON logs**
- [x]  **Integrate Swagger UI JWT support**
- [x]  **Dockerize the app**
- [x]  **Add environment-based config**
- [x]  **Implement Alembic migrations** *(optional)*

---

## 🧭 Week 1: Secure REST API — User Authentication (FastAPI + JWT)

### 🎯 Overview

Set up a backend that lets users **register**, **log in**, and **receive JWT tokens** for authenticated requests.

By the end of the week, you’ll have a functioning `/register` and `/login` system with hashed passwords and token issuance.

### 🧱 **Core Tasks**

🧩 1. Environment & Setup

**Objective:** Get your local environment ready for development.

**Tasks**

- [x]  Install dependencies

```jsx
pip install fastapi uvicorn python-jose[cryptography] passlib[bcrypt] sqlalchemy
```

- [x]  Create a project folder:

```jsx
secure_rest_api/
├── main.py
├── models.py
├── database.py
├── schemas.py
├── auth.py
└── requirements.txt

```

- [x]  Set up a simple SQLite database using SQLAlchemy.

🧩 2. Define User Model & Schema

**Objective:** Represent users in both database and API.

**Tasks**

- [x]  Create a `User` table (`id`, `username`, `email`, `hashed_password`).
- [x]  Define Pydantic schemas:
    - `UserCreate` for incoming registration data.
    - `UserOut` for safe response output (no password).
- [x]  Write DB initialization logic in `database.py`.
- Initialize the Database: 
Use this code snippet once to **create the tables** in your SQLite database below:

database.py: 
This file manages the **database connection** and **session lifecycle**.

```jsx
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
```

Schemas.py:  file defines the structure of data for creating and representing a user in an application, using the Pydantic library. These Pydantic models, or "schemas," are primarily used for data validation and serialization, especially in the context of APIs built with frameworks like FastAPI.

**orm_mode = True**: This is a powerful feature that allows the Pydantic model to be created from an ORM (Object-Relational Mapping) model, such as a SQLAlchemy object. When orm_mode is enabled, Pydantic will try to read the values of the fields from the attributes of the ORM object (e.g., [user.id](http://user.id/), user.username) instead of just from a dictionary. This makes it seamless to convert a database record into a Pydantic model that can then be sent as a response from your API.

```jsx
# schemas.py
from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: int
    username: str
    email: EmailStr

		try:
    # Pydantic v2
        class Config:
            from_attributes = True
    except:
    # Pydantic v1 fallback
        class Config:
            orm_mode = True

```

Define your database models (tables) using SQLAlchemy ORM.

Sample ([models.py](http://models.py/)):  file defines the **structure of your data at rest** (how it's stored permanently in the database)

- You're creating a table named users.
- That table has four columns: id, username, email, and hashed_password.
- You've set rules for these columns, like making the id, username, and email unique.

```jsx
from sqlalchemy import Column, Integer, String
from database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)

```

Use this code snippet once to **create the tables** in your SQLite database.

```python
# create_db.py
from database import Base, engine
from models import User

print("Creating database tables...")
Base.metadata.create_all(bind=engine)
print("Database initialized successfully!")

```

```jsx
python create_db.py
```

How to check your SQLite database structure using the `sqlite3` CLI:

```jsx
sqlite3 test.db
.tables
.schema users
.exit
```

🧩 3. Implement Password Hashing

**Objective:** Ensure all stored passwords are hashed, not plain text.

**Tasks**

- [x]  Use **bcrypt** via Passlib for secure hashing.
- [x]  Add helper functions in `auth.py`:

```jsx
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

```

- [x]  Hash password before storing it in the `/register` route.

🧩 4. JWT Token Creation

**Objective:** Create and verify JWTs for sessionless authentication.

**Tasks**

- [x]  Use **python-jose** to create JWTs with an expiration claim.
- [x]  Store your secret key & algorithm constants in `.env`.

```jsx
SECRET_KEY = "supersecretkey"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

```

Tip:

For production, use a strong random secret:

```jsx
python -c "import secrets; print(secrets.token_hex(32))"
```

- [x]  Add helper functions:

```jsx
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

```

🧩 5. Register & Login Routes

**Objective:** Let users register and log in to get tokens.

**Tasks**

- [x]  `/register` — create user with hashed password
- [x]  `/login` — verify password and issue JWT
- [x]  Return `{"access_token": token, "token_type": "bearer"}`

```jsx
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

```

 **Learning Outcomes**

By the end of Week 1, you will:

✅ Understand how JWT-based authentication works

✅ Know how to securely hash and verify passwords

✅ Be able to register and log in users safely

✅ Gain experience with authentication dependencies and error handling

### 🧾 **Deliverable**

A FastAPI project that supports:

- `/register`: create new users
- `/login`: issue JWT token
- Token verification via Bearer header
- Database-backed user storage

## 🧭 Week 2 — Protected CRUD API & Security Enhancements

### 🎯 Overview

You’ll evolve your Week 1 authentication system into a **secure, production-ready FastAPI backend** with protected CRUD endpoints, token expiry, and better observability.

### ✅ Goals

- Secure all CRUD routes with JWT authentication
- Enforce access control per user (and optionally by role)
- Implement token expiry + refresh
- Add request/response logging for auditing and debugging

### 🧱 Core Tasks

|  | Task | Description | Deliverable |
| --- | --- | --- | --- |
| ✅ | **Create `Item` model** | Add `title`, `description`, `owner_id` to SQLAlchemy models | `models.py` |
| ✅ | **Add `/items` CRUD endpoints** | Implement `GET`, `POST`, `PUT`, `DELETE` routes | `main.py` |
| ✅ | **Protect routes with JWT** | Add `Depends(get_current_user)` to each CRUD route | All CRUD routes |
| ✅ | **Return 401 on invalid/expired token** | Catch JWTError in `get_current_user()` | Consistent auth failure handling |
| ✅ | **Implement token expiry & refresh** | Set token to expire (e.g. 15 min) + add `/refresh` endpoint | JWT refresh workflow |
| ✅ | **Add role-based access control** | Add optional `is_admin` field → admin-only routes | User roles |
| ✅ | **Add logging middleware** | Log each request & response with timestamps | `middlewares/logging.py` or `main.py` |

### ⚙️ Implementation Breakdown

1️⃣ `Item` Model

```jsx
class Item (Base):
    __tablename__ = "items"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String)
    owner_id = Column(Integer, ForeignKey("users.id"))
    
    # Relationship — link Item → User
    owner = relationship("User", back_populates="items")
    
```

`Item` Schema

```jsx
# schemas.py
from pydantic import BaseModel, EmailStr
from typing import Optional

# --- User Schema ----
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: int
    username: str
    email: EmailStr

    model_config = ConfigDict(from_attributes=True)

# --- New Item Schema ---
class ItemCreate(BaseModel):
    title: str
    description: Optional[str] = None
    
class ItemOut(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    owner_id: int
    
    model_config = ConfigDict(from_attributes=True)
```

2️⃣ CRUD Routes

- `POST /items` → create item for current user
- `GET /items` → fetch user’s own items
- `PUT /items/{id}` → update item (ownership check)
- `DELETE /items/{id}` → delete item (ownership check)

```jsx
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
```

Each route includes:

```jsx
current_user: User = Depends(get_current_user)
```

3️⃣ Token Expiry & Refresh

- Add `ACCESS_TOKEN_EXPIRE_MINUTES = 15`
- Create `/refresh` endpoint that issues a new token if the old one is valid but near expiry.

```jsx
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
```

4️⃣ Role-Based Access

Add a column to your `User` model:

```jsx
is_admin = Column(Boolean, default=False)
```

Example check:

```jsx
if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
```

5️⃣ Logging Middleware

logging.py:

```jsx
import logging
import os
import time
from logging.handlers import TimedRotatingFileHandler

from dotenv import load_dotenv
from jose import JWTError, jwt
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from middlewares.json_logger import JsonFormatter
import uuid

env = os.getenv("ENV", "dev")
load_dotenv(f".env.{env}")

SECRET_KEY = os.getenv("SECRET_KEY", "")
ALGORITHM = os.getenv("ALGORITHM", "HS256")

if not os.path.exists("logs"):
    os.makedirs("logs")

json_formatter = JsonFormatter()

# --- Handlers (daily rotation) ---
access_handler = TimedRotatingFileHandler("logs/app.log", when="midnight", backupCount=7)
error_handler = TimedRotatingFileHandler("logs/error.log", when="midnight", backupCount=7)

access_handler.setFormatter(json_formatter)
error_handler.setFormatter(json_formatter)

# --- Loggers ---
access_logger = logging.getLogger("access_logger")
access_logger.setLevel(logging.INFO)
access_logger.propagate = False
if not access_logger.handlers:
    access_logger.addHandler(access_handler)

error_logger = logging.getLogger("error_logger")
error_logger.setLevel(logging.ERROR)
error_logger.propagate = False
if not error_logger.handlers:
    error_logger.addHandler(error_handler)

# --- Optional: Console logs in debug ---
if os.getenv("DEBUG", "False").lower() == "true":
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(json_formatter)
    access_logger.addHandler(console_handler)
    error_logger.addHandler(console_handler)

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        method = request.method
        path = request.url.path
        user = "anonymous"
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id

        # Skip sensitive routes (login/register)
        if path in ["/login", "/register"]:
            response = await call_next(request)
            return response

        # Decode JWT for username
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            try:
                payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
                user = payload.get("sub", "unknown")
            except JWTError:
                user = "invalid_token"

        try:
            response: Response = await call_next(request)
            process_time = time.time() - start_time
            log_fields = {
                "env": env,
                "request_id": request_id,
                "user": user,
                "path": path,
                "method": method,
                "status_code": response.status_code,
                "process_time": round(process_time, 4),
            }

            if response.status_code >= 400:
                error_logger.error("request_completed", extra=log_fields)
            else:
                access_logger.info("request_completed", extra=log_fields)

            return response

        except Exception as e:
            process_time = time.time() - start_time
            error_fields = {
                "env": env,
                "request_id": request_id,
                "user": user,
                "path": path,
                "method": method,
                "status_code": 500,
                "process_time": round(process_time, 4),
                "exception": repr(e),
            }
            error_logger.error("request_failed", extra=error_fields)
            raise e

```

error_handler.py

```jsx
# middlewares/error_handler.py
import time
import logging
import traceback
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

error_logger = logging.getLogger("error_logger")

class ExceptionLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        try:
            response = await call_next(request)
            return response
        
        # Handle FastAPI-defined exceptions (e.g. 401, 404)
        except HTTPException as http_exc:
            process_time = time.time() - start_time
            request_id = getattr(request.state, "request_id", None)
            error_logger.error(
                f"HTTPException {http_exc.status_code} | {request.method} {request.url.path} | "
                f"Request ID: {request_id} | Detail: {http_exc.detail} | {process_time:.2f}s"
            )
            return JSONResponse(
                status_code=http_exc.status_code,
                content={
                    "detail": http_exc.detail,
                    "request_id": request_id
                },
                headers=http_exc.headers or {},
            )

        except Exception as e:
            process_time = time.time() - start_time
            tb = traceback.format_exc()
            request_id = getattr(request.state, "request_id", None)
            error_logger.error(
                f"Exception on {request.method} {request.url.path} | "
                f"Request ID: {request_id} | {process_time:.2f}s | {repr(e)}\n{tb}"
            )

            # Handle unexpected server errors (500)
            return JSONResponse(
                status_code=500,
                content={
                    "detail": "Internal Server Error", 
                    "request_id": request_id
                },
            )

```

Add in main.py:

```jsx
from middlewares.logging import LoggingMiddleware
from middlewares.error_handler import ExceptionLoggingMiddleware

app = FastAPI()
app.add_middleware(ExceptionLoggingMiddleware)
app.add_middleware(LoggingMiddleware)

```

### 🧾 Deliverables

✅ FastAPI backend with token-secured CRUD

✅ JWT auth + token expiry

✅ Role-based and ownership-based access control

✅ Centralized logging

✅ Swagger documentation

## 🧭 Week 3: Advanced API Hardening & DevOps Setup

### 🎯 Overview

In Week 3, your goal is to take your Secure REST API from a functional prototype to a

**production-ready** backend. You’ll implement **rate limiting, health checks, structured logging, environment-based configuration, and Dockerization** By the end of the week, your API will be

**secure, observable, scalable, and ready for deployment**

### ✅ Goals

- Improve reliability and error visibility.
- Protect endpoints against abuse (rate limiting).
- Enable monitoring and diagnostics.
- Prepare the API for containerized deployment (Docker).
- Separate development and production configurations.

### 🧱 **Core Tasks**

| ✅ | Task | Description | Deliverable |
| --- | --- | --- | --- |
| ✅ | **Add rate limiting** | Prevent API abuse using `slowapi` or custom middleware. | `middlewares/rate_limit.py` |
| ✅ | **Add API health check** | Create `/health` endpoint to verify DB and server status. | `/health` route |
| ✅ | **Add structured JSON logs** | Convert logs into JSON for Docker and cloud readability. | `middlewares/logging.py` update |
| ✅ | **Integrate Swagger UI JWT support** | Add an “Authorize” button to Swagger for token use. | `/docs` with Bearer auth |
| ✅ | **Dockerize the app** | Add `Dockerfile` and `docker-compose.yml` for container deployment. | Containerized app |
| ✅ | **Add environment-based config** | Separate `.env.dev` and `.env.prod` for safe config management. | Environment files |
| ✅ | **Implement Alembic migrations** *(optional)* | Handle DB schema updates without deleting data. | `alembic/` folder |

### 🧩 **Implementation Guide**

1. Rate Limiting Middleware (basic example)

Install dependency:

```jsx
pip install slowapi
```

Create file: `middlewares/rate_limit.py`

```jsx
from slowapi import Limiter
from slowapi.util import get_remote_address
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

# limiter = Limiter(key_func=get_remote_address)
# Default: 5 requests per minute per IP
limiter = Limiter(key_func=get_remote_address, default_limits=["5/minute"])

def register_rate_limiter(app: FastAPI):
    app.state.limiter = limiter
    app.add_middleware(SlowAPIMiddleware)

    @app.exception_handler(RateLimitExceeded)
    async def rate_limit_exceeded(request: Request, exc: RateLimitExceeded):
        return JSONResponse(status_code=429, content={"detail": "Too many requests"})
```

Add to [main.py](http://main.py/):

```jsx
from middlewares.rate_limit import register_rate_limiter, limiter
register_rate_limiter(app)

@app.post("/login")
@limiter.limit(LOGIN_RATE_LIMIT)
def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):....

@app.get("/items", response_model=list[ItemOut])
@limiter.limit(ITEMS_RATE_LIMIT)
def get_items(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):....

```

Add Refresh Token for Authentication:

```jsx
# --- Refresh Token Creation ---
def create_refresh_token(data: dict):
    """
    Creates a long-lived refresh token (default: 7 days).
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    refresh_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return refresh_jwt
```

2. Health Check Endpoint

```jsx
# Health check route — no limit
@app.get("/health")
@limiter.exempt
def health_check(db: Session = Depends(get_db)):
    try:
        db.execute("SELECT 1")
        return {"status": "healthy"}
    except Exception:
        raise HTTPException(status_code=503, detail="Database unavailable")
```

3. Structured JSON logs format

```jsx
import json
import logging

class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_entry = {
            "time": self.formatTime(record, "%Y-%m-%d %H:%M:%S"),
            "level": record.levelname,
            "message": record.getMessage(),
        }

        # Add extra context if present
        if hasattr(record, "user"):
            log_entry["user"] = record.user
        if hasattr(record, "path"):
            log_entry["path"] = record.path
        if hasattr(record, "method"):
            log_entry["method"] = record.method
        if hasattr(record, "status_code"):
            log_entry["status_code"] = record.status_code
        if hasattr(record, "process_time"):
            log_entry["process_time"] = getattr(record, "process_time")
        if hasattr(record, "exception"):
            log_entry["exception"] = record.exception

        return json.dumps(log_entry)
```

4. Swagger UI JWT support

This enables the “Authorize 🔒” button in `/docs` so you can test secured endpoints.

Add this to the *bottom* of your `main.py`:

```jsx
# main.py (add at the end)
from fastapi.openapi.utils import get_openapi

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Secure REST API",
        version="1.0.0",
        description="JWT-secured CRUD API with rate limiting and structured logs.",
        routes=app.routes,
    )
    # Add global JWT (Bearer) security definition
    openapi_schema["components"] = openapi_schema.get("components", {})
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }
    openapi_schema["security"] = [{"BearerAuth": []}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi
```

Added in oauth2.py

```jsx
from fastapi.security import OAuth2PasswordBearer
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
```

✅ FastAPI automatically adds an “Authorize” button to /docs
Paste your JWT token (from /login) there → access secured endpoints in Swagger.

✅ Now when you run:

```jsx
uvicorn main:app --reload
```

→ go to http://127.0.0.1:8000/docs

→ You’ll see the **“Authorize”** button.

Paste your access token (without `Bearer`  prefix).

5. Dockerize the API

Create two files at the project root.

Dockerfile

```jsx
# ---------- Base Image ----------
FROM python:3.10-slim AS base

# ---------- Set working directory ----------
WORKDIR /app

# ---------- Environment Variables ----------
# Prevent Python from writing pyc files and buffer logs
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# ---------- Install dependencies ----------
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir -r requirements.txt

# ---------- Copy Application Code ----------
COPY . .

# ---------- Optional Environment Config ----------
# Control whether Alembic migrations should run at startup
ENV RUN_MIGRATIONS=true
# Optional seed flag for initial admin data
ENV RUN_SEED=false

# Expose FastAPI port
EXPOSE 8000

# ---------- Startup Command ----------
# Copy entrypoint script
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Use JSON format for CMD
CMD ["./entrypoint.sh"]

```

docker-compose.dev.yml

```jsx
version: "3.9"

services:
  api:
    build: .
    container_name: secure_rest_api_dev
    ports:
      - "8000:8000"
    env_file:
      - .env.dev
    environment:
      - ENV=dev
      - RUN_MIGRATIONS=true
      - RUN_SEED=true       # useful for local dev testing
    volumes:
      - .:/app              # live code updates (hot reload)
      - dev_db:/data        # persistent local DB
    command: uvicorn main:app --host 0.0.0.0 --port 8000 --reload
    restart: always

volumes:
  dev_db:
```

docker-compose.prod.yml

```jsx
version: "3.9"

services:
  api:
    build: .
    container_name: secure_rest_api_prod
    ports:
      - "8000:8000"
    env_file:
      - .env.prod
    environment:
      - ENV=prod
    volumes:
      - app_data:/data     # mount /data for persistent DB storage
    restart: unless-stopped

volumes:
  app_data:

```

Run with:

```jsx
docker compose up --build
```

Now your API is containerized 🎉

6. Environment-based Config

.env.dev

```jsx
DEBUG=True
DATABASE_URL=sqlite:///./test.db
SECRET_KEY=dev-secret
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_MINUTES=43200
DEFAULT_RATE_LIMIT=5/minute
LOGIN_RATE_LIMIT=5/minute
ITEMS_RATE_LIMIT=10/minute
RUN_MIGRATIONS=true
RUN_SEED=true
RUN_MIGRATIONS_ON_STARTUP=true
```

.env.prod

```jsx
DEBUG=False
# Use a mounted volume path or external DB in production
DATABASE_URL=sqlite:////data/app.db
SECRET_KEY=${PROD_SECRET_KEY}
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_MINUTES=43200
DEFAULT_RATE_LIMIT=5/minute
LOGIN_RATE_LIMIT=5/minute
ITEMS_RATE_LIMIT=10/minute
RUN_MIGRATIONS_ON_STARTUP=false
RUN_MIGRATIONS=true
RUN_SEED=false

```

Config:

You’ll use one `config.py` file that automatically loads `.env.dev` or `.env.prod`.

```jsx
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
```

Then update your **`oauth2.py`** to import from config instead of `.env`:

```jsx
# oauth2.py
from config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
```

Run the app again and it will automatically use `.env.dev`.

To switch to production:

```jsx
export ENV=prod
```

7. **Alembic Migrations**

**Alembic** is a database migration tool for SQLAlchemy that allows you to track and version database schema changes over time. Instead of dropping and recreating tables (which loses data), Alembic lets you safely evolve your database schema while preserving existing data.

Installation

```jsx
pip install alembic
```

Initialize

```jsx
alembic init alembic
```

This Create:

```jsx
alembic/
    env.py
    versions/
alembic.ini
```

Edit alembic.ini

Find this line and replace with:

```jsx
sqlalchemy.url = sqlite:///./test.db
```

Edit `alembic/env.py`

Find this line and replace with:

```jsx
from database import Base
from config import DATABASE_URL
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

config.set_main_option("sqlalchemy.url", DATABASE_URL)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
# target_metadata = None
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    
    url = DATABASE_URL
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

```

Then in `run_migrations_online()`:

```jsx
def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),  # ✅ Use alembic.ini section
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

```

That will read `sqlalchemy.url = sqlite:///./test.db` from your `.ini` file.

✅ This is fine for local development,

⚠️ but it can get out of sync with your FastAPI `.env` when you move to production.

Create initial migration:

```jsx
alembic revision --autogenerate -m "create users and items tables"
```

You should see:

```jsx
INFO  [alembic.runtime.migration] Context impl SQLiteImpl.
INFO  [alembic.runtime.migration] Will assume non-transactional DDL.
Generating alembic/versions/20251029_create_users_and_items_tables.py ... done
```

Apply migration

```jsx
alembic upgrade head
```

✅ Now your database schema is version-controlled.

Automating Alembic migrations:

It ensures your database schema stays in sync with your SQLAlchemy models **every time you change them**, without you having to manually run:

```jsx
alembic revision --autogenerate -m "..."
```

Let’s walk through exactly how to set it up — safely, cleanly, and compatible with your FastAPI app and environment setup.

🧩 GOAL

Make Alembic automatically:

1. Detect model changes.
2. Generate a migration file.
3. Apply it (`upgrade head`) automatically — when you start the app or run a script.

Create a Script for Auto-Migrations

In your project root (same level as `main.py`), create a file called:

```jsx
auto_migrate.py
```

and add this:

```jsx
import os
import sys
from alembic.config import Config
from alembic import command
from datetime import datetime

# Point Alembic to the config file
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
alembic_cfg = Config(os.path.join(BASE_DIR, "alembic.ini"))

# Generate timestamp-based migration names
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
message = f"autogen_{timestamp}"

def run_autogenerate():
    print("🔍 Running Alembic autogenerate...")
    command.revision(alembic_cfg, message=message, autogenerate=True)
    print("✅ Autogenerate complete.")

def run_upgrade():
    print("🚀 Applying latest migrations...")
    command.upgrade(alembic_cfg, "head")
    print("✅ Database is up-to-date.")

if __name__ == "__main__":
    try:
        run_autogenerate()
        run_upgrade()
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        sys.exit(1)

```

Run It Manually (Test)

Run the following inside your virtual environment:

```jsx
python auto_migrate.py
```

If everything’s configured correctly, you’ll see:

```jsx
🔍 Running Alembic autogenerate...
✅ Autogenerate complete.
🚀 Applying latest migrations...
✅ Database is up-to-date.
```

✅ That confirms Alembic successfully:

- Compared your models vs. DB schema
- Created a new migration file under `alembic/versions/`
- Upgraded to the latest schema

Add Automatic Migration on App Startup

If you want your FastAPI app to **auto-sync the DB when it boots**, modify your `main.py` like this:
At the very top (after your imports):

```jsx
import os
from alembic.config import Config
from alembic import command
```

Then, right **after creating the `app = FastAPI()`**, add:

```jsx
# --- Auto-run Alembic migrations on startup ---
def run_migrations_on_startup():
    print("🗄️  Running Alembic migrations on startup...")
    alembic_cfg = Config(os.path.join(os.path.dirname(__file__), "alembic.ini"))
    command.upgrade(alembic_cfg, "head")
    print("✅ Database is up-to-date.")

run_migrations_on_startup()

```

Now every time you start the FastAPI app (uvicorn main:app --reload or Docker start), it ensures your database is upgraded to the latest schema automatically.

(This **does not autogenerate**; it just applies the most recent migration.)

If You Want *Fully Automated* Workflow
To make it truly “hands-free” (detect + generate + apply) whenever models change:

- Add this line to your **dev Dockerfile** or local `startup.sh` script:

```jsx
python auto_migrate.py || echo "⚠️ Migration generation failed"
```

That way, every container boot (or dev run) regenerates and applies migrations automatically.

Git Ignore Tip:

Since Alembic creates one migration file per model change, you may want to add this pattern to `.gitignore` if you don’t want local autogen revisions cluttering version control:

```jsx
# Ignore automatically generated Alembic revisions
alembic/versions/autogen_*.py
```

Example Output

```jsx
🔍 Running Alembic autogenerate...
INFO  [alembic.autogenerate.compare] Detected added table 'items'
INFO  [alembic.autogenerate.compare] Detected added table 'users'
  Generating alembic/versions/20251029_214300_autogen_20251029_214300.py ... done
✅ Autogenerate complete.
🚀 Applying latest migrations...
✅ Database is up-to-date.
```

✅ That confirms Alembic successfully:

- Compared your models vs. DB schema
- Created a new migration file under `alembic/versions/`
- Upgraded to the latest schema

Add Automatic Migration on App Startup (Optional)

If you want your FastAPI app to **auto-sync the DB when it boots**, modify your `main.py` like this:
At the very top (after your imports):

```jsx
import os
from alembic.config import Config
from alembic import command
```

Then, right **after creating the `app = FastAPI()`**, add:

```jsx
# --- Auto-run Alembic migrations on startup ---
def run_migrations_on_startup():
    print("🗄️  Running Alembic migrations on startup...")
    alembic_cfg = Config(os.path.join(os.path.dirname(__file__), "alembic.ini"))
    command.upgrade(alembic_cfg, "head")
    print("✅ Database is up-to-date.")

run_migrations_on_startup()
```

Now every time you start the FastAPI app (uvicorn main:app --reload or Docker start),
it ensures your database is upgraded to the latest schema automatically.
(This does not autogenerate; it just applies the most recent migration.)

Fully Automated Workflow:

To make it truly “hands-free” (detect + generate + apply) whenever models change:
Add this line to your **dev Dockerfile** or local `startup.sh` script:

```jsx
python auto_migrate.py || echo "⚠️ Migration generation failed"
```

That way, every container boot (or dev run) regenerates and applies migrations automatically.

(Optional) Git Ignore Tip
Since Alembic creates one migration file per model change, you may want to add this pattern to `.gitignore` if you don’t want local autogen revisions cluttering version control:

```jsx
# Ignore automatically generated Alembic revisions
alembic/versions/autogen_*.py
```

Automatically run `alembic upgrade head` on app startup:

Automatically running Alembic migrations at FastAPI startup ensures your database schema always matches your models in any environment (local, Docker, or production).

🧩 Goal

When FastAPI starts:

1. It runs `alembic upgrade head`
2. Applies all pending migrations automatically
3. Starts serving requests normally

Step 1. Import Alembic in `main.py`

At the **top of your `main.py`**, add these imports:

```jsx
import os
from alembic.config import Config
from alembic import command
```

Step 2. Define the auto-migration function

Right after creating your app in main.py

```jsx
app = FastAPI()
```

add this:

```jsx
def run_migrations_on_startup():
    """
    Automatically apply Alembic migrations at startup.
    This keeps the DB schema in sync with your SQLAlchemy models.
    """
    print("🗄️  Running Alembic migrations on startup...")
    alembic_cfg = Config(os.path.join(os.path.dirname(__file__), "alembic.ini"))
    alembic_cfg.set_main_option("script_location", "alembic")
    command.upgrade(alembic_cfg, "head")
    print("✅ Database is up-to-date.")

```

Then trigger it inside the FastAPI startup event:

```jsx
@app.on_event("startup")
def startup_event():
    run_migrations_on_startup()
```

Run and test:

```jsx
uvicorn main:app --reload
```

Expected log output:

```jsx
🗄️  Running Alembic migrations on startup...
INFO  [alembic.runtime.migration] Context impl SQLiteImpl.
INFO  [alembic.runtime.migration] Will assume non-transactional DDL.
✅ Database is up-to-date.
```

If migrations are already applied, Alembic will simply print “Database is up-to-date” and start normally.

Notes for Production / Docker:

Safe (recommended):

Keep this auto-migrate startup in your app for **dev, staging, and small deployments**.It ensures developers never forget migrations.

Manual control (for production):

In large-scale deployments, instead of running on every container start, you can move it to an **entrypoint script** in Docker:

Dockerfile:

```jsx
CMD ["bash", "-c", "alembic upgrade head && uvicorn main:app --host 0.0.0.0 --port 8000"]
```

This runs migrations **once before** FastAPI starts serving requests.

Make it environment-safe:

To prevent running migrations automatically in production, you can guard it:

```jsx
import os

@app.on_event("startup")
def startup_event():
    if os.getenv("RUN_MIGRATIONS", "true").lower() == "true":
        run_migrations_on_startup()
```

Then in production:

```jsx
export RUN_MIGRATIONS=false
```

or in Docker:

```jsx
environment:
  - RUN_MIGRATIONS=false
```

**Docker setup automatically run Alembic migrations** before FastAPI starts.
This is the best practice for production and deployment pipelines — clean, reliable, and environment-safe.

🧩 Goal

When your Docker container starts:

1. It runs `alembic upgrade head` (applies pending migrations).
2. Then it launches `uvicorn main:app`.

That way, your database is always in sync with your models before the API starts serving requests.

Update your `Dockerfile`
Here’s a **production-ready Dockerfile** (assuming your project is `secure_rest_api/`):

```jsx
# ---------- Base Image ----------
FROM python:3.10-slim AS base

# ---------- Set working directory ----------
WORKDIR /app

# ---------- Environment Variables ----------
# Prevent Python from writing pyc files and buffer logs
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# ---------- Install dependencies ----------
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir -r requirements.txt

# ---------- Copy Application Code ----------
COPY . .

# ---------- Optional Environment Config ----------
# Control whether Alembic migrations should run at startup
ENV RUN_MIGRATIONS=true
# Optional seed flag for initial admin data
ENV RUN_SEED=false

# Expose FastAPI port
EXPOSE 8000

# ---------- Startup Command ----------
# Runs Alembic migrations (if enabled), optionally seeds DB, then starts FastAPI
CMD if [ "$RUN_MIGRATIONS" = "true" ]; then \
        echo "🗄️  Running Alembic migrations..." && \
        alembic upgrade head && \
        echo "✅ Database up-to-date."; \
    fi && \
    if [ "$RUN_SEED" = "true" ]; then \
        echo "🌱 Running database seed..." && \
        python seed_data.py && \
        echo "✅ Seeding complete."; \
    fi && \
    echo "🚀 Starting FastAPI..." && \
    uvicorn main:app --host 0.0.0.0 --port 8000

```

🧠 How this works

- RUN_MIGRATIONS=true (default) runs migrations every time the container starts.
- If you set RUN_MIGRATIONS=false, it will skip Alembic and go straight to uvicorn.

You can override it at runtime:

```jsx
docker run -e RUN_MIGRATIONS=false secure-rest-api:prod
```

Ensure Alembic is in requirements.txt

Check your `requirements.txt` includes:

```jsx
alembic
sqlalchemy
fastapi
uvicorn
python-dotenv
jose
```

If missing, add and rebuild:

```jsx
docker compose build
```

Update your docker-compose.prod.yml

```jsx
version: "3.9"

services:
  api:
    build: .
    container_name: secure_rest_api
    ports:
      - "8000:8000"
    env_file:
      - .env.prod
    environment:
      - ENV=prod
      - RUN_MIGRATIONS=true
    restart: unless-stopped

```

Build and run:

Build your image:

```jsx
docker compose -f docker-compose.prod.yml build
```

Run it:

```jsx
docker compose -f docker-compose.prod.yml up
```

Expected startup logs:

```jsx
🗄️  Running Alembic migrations...
INFO  [alembic.runtime.migration] Context impl SQLiteImpl.
INFO  [alembic.runtime.migration] Will assume non-transactional DDL.
✅ Database up-to-date.
🚀 Starting FastAPI...
INFO:     Started server process [1]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000

```

✅ Confirm the DB is migrated before app startup.

Step 5. Optional: Safety guard for production

In large deployments, it’s safer to **run Alembic once** rather than on every container restart (to avoid race conditions in multi-instance setups).

OptionA: Run migrations manually (one-time)

```jsx
docker compose -f docker-compose.prod.yml run api alembic upgrade head
```

Then launch normally:

```jsx
docker compose -f docker-compose.prod.yml up -d
```

Option B — Keep migrations automatic but conditional

Use a startup lock file:

```jsx
CMD if [ ! -f /tmp/migrated.lock ]; then \
        alembic upgrade head && touch /tmp/migrated.lock; \
    fi && \
    uvicorn main:app --host 0.0.0.0 --port 8000

```

→ prevents migrations from running twice in clustered setups.

docker-compose.prod.yml

```jsx
version: "3.9"

services:
  api:
    build: .
    container_name: secure_rest_api
    ports:
      - "8000:8000"
    env_file:
      - .env.prod
    environment:
      - ENV=prod
      - RUN_MIGRATIONS=true      # auto-run Alembic
      - RUN_SEED=true            # (optional) seed data
    restart: unless-stopped

```

Add a `seed_data.py`
If you want to automatically create an **admin user** after migrations (great for dev/prod initialization), create `seed_data.py` in your project root:

```jsx
# seed_data.py
from database import SessionLocal
from models import User, Item
from auth import hash_password

def seed_admin_user():
    db = SessionLocal()
    try:
        # Check if admin already exists
        existing_admin = db.query(User).filter(User.username == "admin").first()
        if existing_admin:
            print("Admin user already exists.")
            return

        # Create admin user
        admin_user = User(
            username="admin",
            email="admin@example.com",
            hashed_password=hash_password("admin123"),  # default password
            is_admin=True,
        )
        db.add(admin_user)
        db.commit()
        print("Admin user created: username=admin, password=admin123")

    except Exception as e:
        print(f"Seeding failed: {e}")
        db.rollback()
    finally:
        db.close()

def seed_demo_items():
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.username == "admin").first()
        if not user:
            print("Skipping item seeding — admin user not found.")
            return

        existing_item = db.query(Item).first()
        if existing_item:
            print("Demo items already exist.")
            return

        item1 = Item(title="Welcome Item", description="Example item for admin", owner_id=user.id)
        item2 = Item(title="Sample Task", description="This is just a demo item", owner_id=user.id)
        db.add_all([item1, item2])
        db.commit()
        print("Demo items created successfully.")

    except Exception as e:
        print(f"Failed to seed demo items: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("Running database seed...")
    seed_admin_user()
    seed_demo_items()
    print("Seeding complete.")

```

Usage

Development

```jsx
docker compose -f docker-compose.dev.yml up --build
```

Production

```jsx
docker compose -f docker-compose.prod.yml up --build -d
```

✅ You’ll see:

```jsx
🗄️  Running Alembic migrations...
✅ Database up-to-date.
🌱 Running database seed...
✅ Admin user created (username=admin)
🚀 Starting FastAPI...
INFO:     Application startup complete.

```

Now let’s finish this setup properly by adding a robust **`entrypoint.sh`** script and explaining how it all ties together.

🧩 Why Use an Entrypoint Script

A separate entrypoint script gives you:

- Clear startup flow (migrations → seeding → app start)
- Easier debugging and future changes
- Better separation between build and runtime logic

Step 1. Create `entrypoint.sh`

In your project root, create this file:

```jsx
#!/bin/bash
set -e  # Exit immediately on error

echo "🚀 Starting container setup..."

# ---------- 1. Run Alembic migrations ----------
if [ "$RUN_MIGRATIONS" = "true" ]; then
  echo "🗄️  Running Alembic migrations..."
  alembic upgrade head
  echo "✅ Alembic migrations complete."
else
  echo "⏭️  Skipping migrations (RUN_MIGRATIONS=$RUN_MIGRATIONS)"
fi

# ---------- 2. Run optional seeding ----------
if [ "$RUN_SEED" = "true" ]; then
  echo "🌱 Running database seed..."
  python seed_data.py
  echo "✅ Database seed complete."
else
  echo "⏭️  Skipping seeding (RUN_SEED=$RUN_SEED)"
fi

# ---------- 3. Start FastAPI ----------
echo "🚀 Launching FastAPI app..."
exec uvicorn main:app --host 0.0.0.0 --port 8000

```

Step 2. Make it executable

In your project root (on your host machine):

```jsx
chmod +x entrypoint.sh
```

If you’re on Windows WSL or Git Bash, also run:

```jsx
git update-index --chmod=+x entrypoint.sh
```

This ensures Docker respects executable permissions when copying.

Verify your Dockerfile

Your current Dockerfile is already perfect for using this script.

Just make sure the last lines are:

```jsx
# Copy and run entrypoint
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

CMD ["./entrypoint.sh"]

```

✅ This ensures your container always starts using the entrypoint script.

Example docker-compose.prod.yml

Here’s how your docker-compose.prod.yml should look now:

```jsx
version: "3.9"

services:
  api:
    build: .
    container_name: secure_rest_api
    ports:
      - "8000:8000"
    env_file:
      - .env.prod
    environment:
      - ENV=prod
      - RUN_MIGRATIONS=true
      - RUN_SEED=true
    restart: unless-stopped

```

Step 5. Example `.env.prod`

```jsx
DEBUG=False
# Use a mounted volume path or external DB in production
DATABASE_URL=sqlite:////data/app.db
SECRET_KEY=7d1fb16d1d4f069f4f2acbae5320b033a41653c4c46c658d03f542bf38558cef
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_MINUTES=43200
DEFAULT_RATE_LIMIT=5/minute
LOGIN_RATE_LIMIT=5/minute
ITEMS_RATE_LIMIT=10/minute
RUN_MIGRATIONS=true
RUN_SEED=false

```

Build and Run

Build the image:

```jsx
docker compose -f docker-compose.prod.yml build
```

Run the container:

```jsx
docker compose -f docker-compose.prod.yml up
```

Expected logs:

```jsx
🚀 Starting container setup...
🗄️  Running Alembic migrations...
✅ Alembic migrations complete.
🌱 Running database seed...
✅ Database seed complete.
🚀 Launching FastAPI app...
INFO:     Uvicorn running on http://0.0.0.0:8000

```

Optional Enhancements

🔹 1. Add a startup lock (to avoid multiple migration runs)

In multi-container setups, wrap the migration command:

```jsx
if [ ! -f /tmp/migrated.lock ]; then
  alembic upgrade head && touch /tmp/migrated.lock
else
  echo "✅ Migrations already applied."
fi

```

🔹 2. Add environment-based startup

If you ever use separate services, you can conditionally run Uvicorn:

```jsx
if [ "$ENV" = "prod" ]; then
  exec uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
else
  exec uvicorn main:app --host 0.0.0.0 --port 8000 --reload
fi

```

✅ **1. Working Rate-Limited API**

- Uses `slowapi` or custom limiter.
- Returns `429 Too Many Requests` on overflow.

✅ **2. Health Check Endpoint**

- `/health` confirms DB + server are operational.

✅ **3. Structured JSON Logging**

- `logs/app.log` → requests, `logs/error.log` → errors.
- JSON format: `{time, level, message}`.

✅ **4. Swagger JWT Integration**

- “Authorize” button visible.
- Authenticated routes testable via Swagger UI.

✅ **5. Dockerized App**

- API runs via container with `docker compose up`.
- Mounted local volume for code updates.

✅ **6. Environment-based Config**

- `.env.dev` (local) and `.env.prod` (deployment).

✅ **7. Alembic Migrations (optional)**

- Versioned DB schema updates using `alembic`.