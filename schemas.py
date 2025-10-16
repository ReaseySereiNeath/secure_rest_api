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

    try:
    # Pydantic v2
        class Config:
            from_attributes = True
    except:
    # Pydantic v1 fallback
        class Config:
            orm_mode = True

# --- New Item Schema ---
class ItemCreate(BaseModel):
    title: str
    description: Optional[str] = None
    
class ItemOut(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    owner_id: int
    
    try:
    # Pydantic v2
        class Config:
            from_attributes = True
    except:
    # Pydantic v1 fallback
        class Config:
            orm_mode = True