import sys
import os

# Create reproducible environment
sys.path.append(os.getcwd())

from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker
from app.db.database import Base
# Import all models
from app.models.user import User
from app.models.video import Video
from app.models.extraction import Extraction
from app.models.notification import Notification
from app.models.email_verification import EmailVerification
from app.models.password_reset import PasswordReset
from app.models.usage_stats import UsageStats

from app.core import security

# Mock JSONB for SQLite
from sqlalchemy.dialects.postgresql import JSONB
import sqlalchemy.dialects.sqlite
sqlalchemy.dialects.sqlite.base.SQLiteTypeCompiler.visit_JSONB = lambda self, type_, **kw: "JSON"

def debug_db():
    print("Debugging DB creation...")
    SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
    )
    
    # Check what tables are registered
    print("Registered tables in Base.metadata:", Base.metadata.tables.keys())
    
    Base.metadata.create_all(bind=engine)
    
    inspector = inspect(engine)
    created_tables = inspector.get_table_names()
    print("Created tables in DB:", created_tables)
    
    if "users" in created_tables:
        print("SUCCESS: users table created")
    else:
        print("FAILURE: users table NOT created")

def debug_hashing():
    print("\nDebugging Password Hashing...")
    password = "password"
    try:
        hashed = security.hash_password(password)
        print(f"Hashing '{password}' successful. Result: {hashed[:10]}...")
    except Exception as e:
        print(f"Hashing '{password}' FAILED: {e}")
        
    long_string = "x" * 100
    try:
        hashed = security.hash_password(long_string)
        print(f"Hashing long string successful.")
    except Exception as e:
        print(f"Hashing long string FAILED: {e}")

if __name__ == "__main__":
    debug_db()
    debug_hashing()
