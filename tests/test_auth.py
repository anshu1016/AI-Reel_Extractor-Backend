from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app import models
from app.core import security

def test_signup_new_user(client: TestClient, override_get_db: None):
    """Test signing up a new user."""
    response = client.post(
        "/api/v1/auth/signup",
        json={
            "email": "newuser@example.com",
            "password": "StrongPassword123!",
            "full_name": "New User",
            "company_name": "Test Company"
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "newuser@example.com"
    assert "id" in data
    assert "password" not in data


def test_signup_existing_email(client: TestClient, override_get_db: None, db_session: Session):
    """Test signing up with an existing email."""
    # Create existing user
    user = models.User(
        email="existing@example.com",
        password_hash=security.hash_password("password"),
        full_name="Existing User",
        usage_stats=models.UsageStats()
    )
    db_session.add(user)
    db_session.commit()
    
    response = client.post(
        "/api/v1/auth/signup",
        json={
            "email": "existing@example.com",
            "password": "NewPassword123!",
            "full_name": "Another User"
        },
    )
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]


def test_login_success(client: TestClient, override_get_db: None, db_session: Session):
    """Test successful login."""
    # Create user
    password = "StrongPassword123!"
    user = models.User(
        email="login@example.com",
        password_hash=security.hash_password(password),
        full_name="Login User",
        account_status="active",
        usage_stats=models.UsageStats()
    )
    db_session.add(user)
    db_session.commit()
    
    # Login
    response = client.post(
        "/api/v1/auth/login/access-token",
        data={
            "username": "login@example.com",
            "password": password
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client: TestClient, override_get_db: None, db_session: Session):
    """Test login with wrong password."""
    # Create user
    user = models.User(
        email="wrongpass@example.com",
        password_hash=security.hash_password("CorrectPassword"),
        full_name="Wrong Pass User",
        usage_stats=models.UsageStats()
    )
    db_session.add(user)
    db_session.commit()
    
    # Login with wrong password
    response = client.post(
        "/api/v1/auth/login/access-token",
        data={
            "username": "wrongpass@example.com",
            "password": "WrongPassword"
        },
    )
    assert response.status_code == 400
    assert "Incorrect email or password" in response.json()["detail"]


def test_password_recovery(client: TestClient, override_get_db: None, db_session: Session):
    """Test password recovery request."""
    # Create user first
    user = models.User(
        email="test@example.com",
        password_hash=security.hash_password("password"),
        full_name="Test User",
        usage_stats=models.UsageStats()
    )
    db_session.add(user)
    db_session.commit()

    response = client.post(
        "/api/v1/auth/password-recovery/test@example.com"
    )
    assert response.status_code == 200
    assert "Password recovery email sent" in response.json()["msg"]
