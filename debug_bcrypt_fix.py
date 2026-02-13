import sys
import os
import bcrypt

# Monkeypatch bcrypt to fix passlib compatibility
# bcrypt 4.0.0 removed __about__
# passlib 1.7.4 depends on it
if not hasattr(bcrypt, "__about__"):
    class About:
        __version__ = bcrypt.__version__
    bcrypt.__about__ = About()

from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def test_hash():
    password = "test"
    try:
        hashed = pwd_context.hash(password)
        print(f"Hashing successful: {hashed[:10]}...")
        assert pwd_context.verify(password, hashed)
        print("Verification successful")
    except Exception as e:
        print(f"Hashing failed: {e}")

if __name__ == "__main__":
    test_hash()
