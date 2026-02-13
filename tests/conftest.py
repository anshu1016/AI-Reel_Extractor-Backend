import pytest
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.db.database import Base, get_db
from app.main import app
# Import all models to ensure they are registered with Base
from app import models

# Use in-memory SQLite for tests
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

from sqlalchemy.pool import StaticPool

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Mock JSONB for SQLite
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.types import JSON
import sqlalchemy.dialects.sqlite

# Patch JSONB to work as JSON in SQLite
sqlalchemy.dialects.sqlite.base.SQLiteTypeCompiler.visit_JSONB = lambda self, type_, **kw: "JSON"


@pytest.fixture(scope="function")
def db_session() -> Generator:
    """
    Create a fresh database session for each test.
    """
    # Import all models to ensure they are registered
    from app.models.user import User
    from app.models.video import Video
    from app.models.extraction import Extraction
    from app.models.notification import Notification
    from app.models.email_verification import EmailVerification
    from app.models.password_reset import PasswordReset
    from app.models.usage_stats import UsageStats
    
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        # Drop tables after test
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="module")
def client() -> Generator:
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="function")
def override_get_db(db_session):
    """
    Override get_db dependency to use the test database session.
    """
    def _override_get_db():
        try:
            yield db_session
        finally:
            pass
            
    app.dependency_overrides[get_db] = _override_get_db
    yield
    app.dependency_overrides = {}
