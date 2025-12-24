from pydantic import BaseModel, EmailStr
from uuid import UUID

# 1. Schema for Registration (Input)
class UserCreate(BaseModel):
    email: EmailStr
    password: str

# 2. Schema for Reading User Data (Output)
# Notice we DO NOT include the password here.
class UserResponse(BaseModel):
    id: UUID
    email: EmailStr
    is_active: bool

    class Config:
        from_attributes = True  # Allows Pydantic to read SQLAlchemy models

# 3. Schema for the JWT Token (Output)
class Token(BaseModel):
    access_token: str
    token_type: str