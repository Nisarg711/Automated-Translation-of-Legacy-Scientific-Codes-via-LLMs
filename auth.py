"""
Authentication helpers for the BMP Translator app.
Provides register/login via bcrypt-hashed passwords stored in Neon Postgres,
and Google OAuth ID-token verification.
"""

import bcrypt
import psycopg2
from pgvector.psycopg2 import register_vector
import os
from dotenv import load_dotenv
import jwt
from datetime import datetime, timedelta, timezone

load_dotenv()

JWT_SECRET = os.environ["JWT_SECRET"]
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_MINUTES = 60

def get_db_connection():
    """Reuse the same Neon Postgres connection pattern from tempbackend."""
    conn = psycopg2.connect(os.environ["NEON_DATABASE_URL"])
    register_vector(conn)
    return conn

def create_access_token(payload: dict) -> str:
    data = payload.copy()
    data["exp"] = datetime.now(timezone.utc) + timedelta(minutes=JWT_EXPIRE_MINUTES)
    data["iat"] = datetime.now(timezone.utc)
    return jwt.encode(data, JWT_SECRET, algorithm=JWT_ALGORITHM)

def verify_access_token(token: str) -> tuple[bool, dict | str]:
    try:
        decoded = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return True, decoded
    except jwt.ExpiredSignatureError:
        return False, "Token expired."
    except jwt.InvalidTokenError:
        return False, "Invalid token."

def authenticate_user_with_token(username: str, password: str) -> tuple[bool, str, str | None]:
    """
    Verify username + password and return a signed JWT on success.
    Returns (True, "", token) on success, or (False, error_message, None) on failure.
    """
    success, message = authenticate_user(username, password)
    if not success:
        return False, message, None

    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, username, email FROM users WHERE username = %s",
                (username.strip(),),
            )
            row = cur.fetchone()
            if row is None:
                return False, "User not found.", None

            user_id, db_username, email = row
            token = create_access_token(
                {
                    "sub": str(user_id),
                    "username": db_username,
                    "email": email,
                    "role": "user",
                }
            )
            return True, "", token
    except Exception as e:
        return False, f"Token creation failed: {str(e)}", None
    finally:
        conn.close()
# ---------------------------------------------------------------------------
# Custom username / password auth
# ---------------------------------------------------------------------------

def register_user(username: str, password: str, email: str = "") -> tuple[bool, str]:
    """
    Register a new user with bcrypt-hashed password.
    Returns (True, "") on success, or (False, error_message) on failure.
    """
    if not username or not password:
        return False, "Username and password are required."
    if len(password) < 4:
        return False, "Password must be at least 4 characters."
    if not email or not email.strip():
        return False, "Email is required."

    password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s)",
                (username.strip(), email.strip(), password_hash),
            )
            conn.commit()
        return True, ""
    except psycopg2.errors.UniqueViolation:
        conn.rollback()
        return False, "Username or email already taken. Please choose another."
    except Exception as e:
        conn.rollback()
        return False, f"Registration failed: {str(e)}"
    finally:
        conn.close()


def authenticate_user(username: str, password: str) -> tuple[bool, str]:
    """
    Verify username + password against the users table.
    Returns (True, "") on success, or (False, error_message) on failure.
    """
    if not username or not password:
        return False, "Username and password are required."

    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT password_hash FROM users WHERE username = %s",
                (username.strip(),),
            )
            row = cur.fetchone()
            if row is None:
                return False, "User not found."

            stored_hash = row[0]
            if bcrypt.checkpw(password.encode("utf-8"), stored_hash.encode("utf-8")):
                return True, ""
            else:
                return False, "Incorrect password."
    except Exception as e:
        return False, f"Login failed: {str(e)}"
    finally:
        conn.close()
