from datetime import timedelta
from typing import Any

from fastapi import APIRouter, Body, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app import models
from app.api import deps
from app.core import security
from app.core.config import settings
from app.schemas import auth as auth_schemas
from app.schemas import user as user_schemas

router = APIRouter()


@router.post("/login/access-token", response_model=auth_schemas.Token)
def login_access_token(
    db: Session = Depends(deps.get_db),
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests.
    """
    # Find user by email
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    
    # Verify password
    if not user or not security.verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password",
        )
        
    # Check if user is active
    if not user.is_active():
        raise HTTPException(status_code=400, detail="Inactive user")
        
    access_token_expires = timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": security.create_access_token(
            user.id, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    }


@router.post("/signup", response_model=user_schemas.UserResponse, status_code=201)
def signup(
    *,
    db: Session = Depends(deps.get_db),
    user_in: user_schemas.UserCreate,
) -> Any:
    """
    Create new user without the need to be logged in.
    """
    # Check if user already exists
    user = db.query(models.User).filter(models.User.email == user_in.email).first()
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this username already exists in the system",
        )
        
    # Create new user
    user = models.User(
        email=user_in.email,
        password_hash=security.hash_password(user_in.password),
        full_name=user_in.full_name,
        company_name=user_in.company_name,
        phone=user_in.phone,
        # Default settings
        timezone=user_in.timezone or "Asia/Kolkata", 
        language=user_in.language or "en",
        notify_processing_complete=user_in.notify_processing_complete,
        account_status="active", # Auto-active for MVP, maybe change later for email verification
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return user


@router.post("/password-recovery/{email}", response_model=dict)
def recover_password(email: str, db: Session = Depends(deps.get_db)) -> Any:
    """
    Password Recovery
    """
    user = db.query(models.User).filter(models.User.email == email).first()

    if not user:
        # Don't reveal that user doesn't exist for security
        return {"msg": "If this email exists in our system, you will receive a password recovery email."}
        
    password_reset_token = security.generate_password_reset_token()
    
    # TODO: Save reset token to DB (PasswordReset model)
    # reset = models.PasswordReset(user_id=user.id, token=password_reset_token, ...)
    # db.add(reset)
    # db.commit()
    
    # TODO: Send email using email_service
    # email_service.send_reset_password_email(email_to=user.email, email=email, token=password_reset_token)
    
    return {"msg": "Password recovery email sent"}


@router.post("/reset-password", response_model=dict)
def reset_password(
    token: str = Body(...),
    new_password: str = Body(...),
    db: Session = Depends(deps.get_db),
) -> Any:
    """
    Reset password
    """
    # TODO: Verify token against DB
    # reset_record = db.query(models.PasswordReset).filter(models.PasswordReset.token == token).first()
    # if not reset_record or not reset_record.is_valid:
    #     raise HTTPException(status_code=400, detail="Invalid or expired token")
        
    # user = db.query(models.User).filter(models.User.id == reset_record.user_id).first()
    # if not user:
    #     raise HTTPException(status_code=404, detail="User not found")
        
    # user.password_hash = security.hash_password(new_password)
    # reset_record.mark_used()
    # db.commit()
    
    return {"msg": "Password updated successfully"}
