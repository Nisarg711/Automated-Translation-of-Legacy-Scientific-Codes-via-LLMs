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

load_dotenv()


def get_db_connection():
    """Reuse the same Neon Postgres connection pattern from tempbackend."""
    conn = psycopg2.connect(os.environ["NEON_DATABASE_URL"])
    register_vector(conn)
    return conn


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
