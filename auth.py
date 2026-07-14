"""
Authentication helpers for the BMP Translator app.
Provides register/login via bcrypt-hashed passwords stored in Neon Postgres,
and Google OAuth ID-token verification.
"""

import bcrypt
import psycopg2
from psycopg2 import pool as pg_pool
import os
from dotenv import load_dotenv
import jwt
from datetime import datetime, timedelta, timezone

load_dotenv()

JWT_SECRET = os.environ["JWT_SECRET"]
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_MINUTES = 60

# A pooled connection avoids paying a fresh TCP+TLS handshake (and Neon's
# serverless cold-start) on every call — this module's functions get hit on
# most Streamlit reruns, not just on meaningful user actions.
_pool = pg_pool.ThreadedConnectionPool(1, 10, dsn=os.environ["NEON_DATABASE_URL"])

def get_db_connection():
    """Check out a pooled connection. Pair with release_db_connection(), not conn.close().
    No register_vector() here — unlike tempbackend.py, none of this module's
    tables (users, translation_threads) store vector columns, and calling it
    costs its own catalog round-trip on every checkout for no benefit.

    Neon suspends its compute (and drops TCP connections) after periods of
    idleness, which leaves stale connections sitting in the pool with no
    client-side signal that they're dead. Pre-ping each checkout and discard
    anything the server has already hung up on, instead of handing callers
    a connection that will blow up on their first query."""
    conn = _pool.getconn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT 1")
        return conn
    except psycopg2.OperationalError:
        _pool.putconn(conn, close=True)
        return _pool.getconn()

def release_db_connection(conn):
    """Return a connection to the pool, or discard it if the server has closed
    it out from under us — putting a dead connection back would just hand it
    to the next caller, who'd hit the same OperationalError."""
    _pool.putconn(conn, close=conn.closed != 0)

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
        release_db_connection(conn)
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
        release_db_connection(conn)


# ---------------------------------------------------------------------------
# Translation thread metadata (sidebar history) — scoped per user
# ---------------------------------------------------------------------------

def upsert_thread(thread_id: str, user_id: str, title: str, source_lang: str, target_lang: str) -> None:
    """Create or update a thread's metadata. Called once, at the moment a translation
    actually runs — not on page load — so browsing/refreshing never litters the
    sidebar with empty placeholder threads. No-op for guests (user_id=None)."""
    if not user_id:
        return
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """INSERT INTO translation_threads (thread_id, user_id, title, source_lang, target_lang)
                   VALUES (%s, %s, %s, %s, %s)
                   ON CONFLICT (thread_id) DO UPDATE
                   SET title = EXCLUDED.title,
                       source_lang = EXCLUDED.source_lang,
                       target_lang = EXCLUDED.target_lang,
                       updated_at = NOW()""",
                (thread_id, user_id, title, source_lang, target_lang),
            )
            conn.commit()
    finally:
        release_db_connection(conn)


def list_threads(user_id: str) -> list[dict]:
    """Return this user's threads, most recently updated first."""
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """SELECT thread_id, title FROM translation_threads
                   WHERE user_id = %s ORDER BY updated_at DESC""",
                (user_id,),
            )
            return [{"thread_id": str(row[0]), "title": row[1]} for row in cur.fetchall()]
    finally:
        release_db_connection(conn)


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
        release_db_connection(conn)
