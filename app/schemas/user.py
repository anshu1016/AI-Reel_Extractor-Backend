from typing import Optional
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field


# Shared properties
class UserBase(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    phone: Optional[str] = None
    company_name: Optional[str] = None
    profile_photo_url: Optional[str] = None
    timezone: Optional[str] = "Asia/Kolkata"
    language: Optional[str] = "en"
    notify_processing_complete: Optional[bool] = True
    notify_processing_failed: Optional[bool] = True
    notify_weekly_summary: Optional[bool] = False
    notify_product_updates: Optional[bool] = False


# Properties to receive via API on creation
class UserCreate(UserBase):
    email: EmailStr
    password: str
    full_name: str


# Properties to receive via API on update
class UserUpdate(UserBase):
    password: Optional[str] = None


# Properties available for API responses
class UserResponse(UserBase):
    id: UUID
    email: EmailStr
    email_verified: bool
    account_status: str
    created_at: datetime
    
    class Config:
        from_attributes = True


# Properties stored in DB
class UserInDB(UserBase):
    id: UUID
    hashed_password: str
    email_verified: bool
    account_status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
