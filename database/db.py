"""
database/db.py
Database connection and operations engine for CROPWISE AI.
Dual-Engine Architecture:
  1. PRODUCTION (Vercel): When DATABASE_URL is set -> Persistent Neon / PostgreSQL.
  2. LOCAL DEVELOPMENT: When DATABASE_URL is absent -> Local SQLite (database/cropwise.db).
Preserves 100% of existing function signatures, data types, and security guarantees.
"""

import os
import sqlite3
import json
import time
from contextlib import contextmanager
from werkzeug.security import generate_password_hash, check_password_hash

import shutil
import tempfile

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_LOCAL_DB = os.path.join(BASE_DIR, "cropwise.db")
SCHEMA_PATH = os.path.join(BASE_DIR, "schema.sql")
POSTGRES_SCHEMA_PATH = os.path.join(BASE_DIR, "postgres_schema.sql")

# Safely load environment variables from .env if present
try:
    from dotenv import load_dotenv
    _project_env = os.path.join(os.path.dirname(BASE_DIR), ".env")
    if os.path.exists(_project_env):
        load_dotenv(dotenv_path=_project_env)
    else:
        load_dotenv()
except Exception:
    pass


SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    mobile TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    farm_location TEXT NOT NULL,
    land_area REAL NOT NULL,
    land_unit TEXT DEFAULT 'Acres',
    preferred_soil TEXT DEFAULT 'Loamy',
    avatar TEXT DEFAULT 'farmer1',
    is_verified INTEGER DEFAULT 1,
    otp_hash TEXT DEFAULT NULL,
    otp_expiry REAL DEFAULT NULL,
    otp_attempts INTEGER DEFAULT 0,
    otp_sent_at REAL DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS recommendations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    soil_type TEXT NOT NULL,
    ph REAL NOT NULL,
    temperature REAL NOT NULL,
    humidity REAL NOT NULL,
    rainfall REAL NOT NULL,
    recommended_crop TEXT NOT NULL,
    variety TEXT DEFAULT 'Standard',
    alternative_crops TEXT DEFAULT '[]',
    decision_notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    expense_date DATE NOT NULL,
    category TEXT NOT NULL,
    amount REAL NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS notes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    tag TEXT DEFAULT 'General',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS reminders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    reminder_date DATE NOT NULL,
    reminder_time TIME NOT NULL DEFAULT '00:00',
    description TEXT DEFAULT '',
    crop TEXT DEFAULT '',
    variety TEXT DEFAULT '',
    category TEXT DEFAULT 'General',
    is_completed INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
"""

POSTGRES_SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    mobile TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    farm_location TEXT NOT NULL,
    land_area DOUBLE PRECISION NOT NULL,
    land_unit TEXT DEFAULT 'Acres',
    preferred_soil TEXT DEFAULT 'Loamy',
    avatar TEXT DEFAULT 'farmer1',
    is_verified INTEGER DEFAULT 1,
    otp_hash TEXT DEFAULT NULL,
    otp_expiry DOUBLE PRECISION DEFAULT NULL,
    otp_attempts INTEGER DEFAULT 0,
    otp_sent_at DOUBLE PRECISION DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS recommendations (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    soil_type TEXT NOT NULL,
    ph DOUBLE PRECISION NOT NULL,
    temperature DOUBLE PRECISION NOT NULL,
    humidity DOUBLE PRECISION NOT NULL,
    rainfall DOUBLE PRECISION NOT NULL,
    recommended_crop TEXT NOT NULL,
    variety TEXT DEFAULT 'Standard',
    alternative_crops TEXT DEFAULT '[]',
    decision_notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS expenses (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    expense_date DATE NOT NULL,
    category TEXT NOT NULL,
    amount DOUBLE PRECISION NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS notes (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    tag TEXT DEFAULT 'General',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS reminders (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    reminder_date DATE NOT NULL,
    reminder_time TIME NOT NULL DEFAULT '00:00',
    description TEXT DEFAULT '',
    crop TEXT DEFAULT '',
    variety TEXT DEFAULT '',
    category TEXT DEFAULT 'General',
    is_completed INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

# -------------------------------------------------------------
# ENGINE DETECTION & CONNECTION HELPERS
# -------------------------------------------------------------

def is_postgres():
    """Returns True if a non-empty DATABASE_URL environment variable is present."""
    url = (os.environ.get("DATABASE_URL") or "").strip()
    return bool(url)


def is_serverless_environment():
    """Check if running in a serverless / read-only runtime like Vercel or AWS Lambda."""
    if (
        os.environ.get("VERCEL")
        or os.environ.get("AWS_LAMBDA_FUNCTION_NAME")
        or os.environ.get("LAMBDA_TASK_ROOT")
        or os.environ.get("AWS_EXECUTION_ENV")
    ):
        return True
    if "/var/task" in BASE_DIR or "/var/runtime" in BASE_DIR:
        return True
    return False


def find_seed_db():
    """Find bundled seed database across possible serverless filesystem locations."""
    candidates = [
        DEFAULT_LOCAL_DB,
        os.path.join(os.getcwd(), "database", "cropwise.db"),
        os.path.join(os.path.dirname(BASE_DIR), "database", "cropwise.db"),
        "/var/task/database/cropwise.db",
    ]
    for p in candidates:
        if os.path.exists(p) and os.path.isfile(p) and os.path.getsize(p) > 0:
            return p
    return None


def get_db_path():
    """Resolves SQLite database path for local/serverless fallback."""
    if os.environ.get("DB_PATH"):
        return os.environ.get("DB_PATH")

    if is_serverless_environment():
        tmp_dir = "/tmp" if os.name != "nt" else tempfile.gettempdir()
        tmp_db = os.path.join(tmp_dir, "cropwise.db")
        if not os.path.exists(tmp_db):
            os.makedirs(tmp_dir, exist_ok=True)
            seed_db = find_seed_db()
            if seed_db:
                try:
                    shutil.copyfile(seed_db, tmp_db)
                    try:
                        os.chmod(tmp_db, 0o666)
                    except Exception:
                        pass
                except Exception as e:
                    print(f"[WARN] Could not copy bundled DB to temp directory: {e}")
        return tmp_db

    return DEFAULT_LOCAL_DB


def get_pg_connection():
    """Establishes a PostgreSQL / Neon connection using RealDictCursor."""
    import psycopg2
    from psycopg2.extras import RealDictCursor

    url = os.environ.get("DATABASE_URL", "").strip()
    if url.startswith("postgres://"):
        url = "postgresql://" + url[len("postgres://"):]

    connect_kwargs = {}
    if "sslmode=" not in url and "localhost" not in url and "127.0.0.1" not in url:
        connect_kwargs["sslmode"] = "require"

    connect_kwargs["keepalives"] = 1
    connect_kwargs["keepalives_idle"] = 30
    connect_kwargs["keepalives_interval"] = 10
    connect_kwargs["keepalives_count"] = 5

    for attempt in range(2):
        try:
            return psycopg2.connect(url, cursor_factory=RealDictCursor, **connect_kwargs)
        except psycopg2.OperationalError as e:
            if attempt == 1:
                raise e
            time.sleep(0.5)



def get_db():
    """SQLite connection factory (retained for direct compatibility)."""
    db_path = get_db_path()
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row

    # Ensure tables exist
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
    if not cursor.fetchone():
        try:
            if os.path.exists(SCHEMA_PATH):
                with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
                    conn.executescript(f.read())
            else:
                conn.executescript(SCHEMA_SQL)
            conn.commit()
        except Exception as e:
            print(f"[WARN] Auto-schema execution note: {e}")

    return conn


def init_db():
    """Initializes schema and tables for active database engine (PostgreSQL or SQLite)."""
    if is_postgres():
        conn = get_pg_connection()
        try:
            with conn.cursor() as cursor:
                if os.path.exists(POSTGRES_SCHEMA_PATH):
                    with open(POSTGRES_SCHEMA_PATH, "r", encoding="utf-8") as f:
                        cursor.execute(f.read())
                else:
                    cursor.execute(POSTGRES_SCHEMA_SQL)
            conn.commit()
            print("[OK] Initialized CROPWISE AI PostgreSQL/Neon database with all tables.")
        except Exception as e:
            print(f"[WARN] PostgreSQL init_db notice: {e}")
        finally:
            conn.close()
        return

    # SQLite initialization
    db_path = get_db_path()
    seed_db = find_seed_db()
    if is_serverless_environment() and not os.path.exists(db_path) and seed_db:
        try:
            os.makedirs(os.path.dirname(db_path), exist_ok=True)
            shutil.copyfile(seed_db, db_path)
            try:
                os.chmod(db_path, 0o666)
            except Exception:
                pass
        except Exception as e:
            print(f"[WARN] Could not copy bundled DB to temp during init: {e}")

    conn = get_db()
    try:
        with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
            conn.executescript(f.read())
    except Exception:
        conn.executescript(SCHEMA_SQL)

    cursor = conn.cursor()
    # Safe migration: ensure 'variety' column exists in 'recommendations'
    cursor.execute("PRAGMA table_info(recommendations)")
    columns = [col["name"] for col in cursor.fetchall()]
    if "variety" not in columns:
        try:
            cursor.execute("ALTER TABLE recommendations ADD COLUMN variety TEXT DEFAULT 'Standard'")
        except Exception as e:
            print(f"[WARN] recommendations.variety migration note: {e}")

    # Safe migration: ensure verification and OTP columns exist in 'users'
    cursor.execute("PRAGMA table_info(users)")
    user_columns = [col["name"] for col in cursor.fetchall()]
    if "is_verified" not in user_columns:
        try:
            cursor.execute("ALTER TABLE users ADD COLUMN is_verified INTEGER DEFAULT 1")
        except Exception as e:
            print(f"[WARN] users.is_verified migration: {e}")
    if "otp_hash" not in user_columns:
        try:
            cursor.execute("ALTER TABLE users ADD COLUMN otp_hash TEXT DEFAULT NULL")
        except Exception as e:
            print(f"[WARN] users.otp_hash migration: {e}")
    if "otp_expiry" not in user_columns:
        try:
            cursor.execute("ALTER TABLE users ADD COLUMN otp_expiry REAL DEFAULT NULL")
        except Exception as e:
            print(f"[WARN] users.otp_expiry migration: {e}")
    if "otp_attempts" not in user_columns:
        try:
            cursor.execute("ALTER TABLE users ADD COLUMN otp_attempts INTEGER DEFAULT 0")
        except Exception as e:
            print(f"[WARN] users.otp_attempts migration: {e}")
    if "otp_sent_at" not in user_columns:
        try:
            cursor.execute("ALTER TABLE users ADD COLUMN otp_sent_at REAL DEFAULT NULL")
        except Exception as e:
            print(f"[WARN] users.otp_sent_at migration: {e}")

    # Safe migration: preserve existing reminders while adding time precision
    cursor.execute("PRAGMA table_info(reminders)")
    reminder_columns = [col["name"] for col in cursor.fetchall()]
    if "reminder_time" not in reminder_columns:
        try:
            cursor.execute("ALTER TABLE reminders ADD COLUMN reminder_time TIME NOT NULL DEFAULT '00:00'")
        except Exception as e:
            print(f"[WARN] reminders.reminder_time migration: {e}")

    conn.commit()
    conn.close()
    print(f"[OK] Initialized CROPWISE AI SQLite database at {db_path} with all tables.")


# -------------------------------------------------------------
# USER MANAGEMENT & AUTHENTICATION
# -------------------------------------------------------------

def create_user(name, mobile, email, password, farm_location, land_area, land_unit="Acres", preferred_soil="Loamy", avatar="farmer1", is_verified=0):
    password_hash = generate_password_hash(password)
    name_clean = name.strip()
    mobile_clean = mobile.strip()
    email_clean = email.strip().lower()
    farm_clean = farm_location.strip()
    area_val = float(land_area)

    if is_postgres():
        import psycopg2
        conn = get_pg_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO users (name, mobile, email, password_hash, farm_location, land_area, land_unit, preferred_soil, avatar, is_verified)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                """, (name_clean, mobile_clean, email_clean, password_hash, farm_clean, area_val, land_unit, preferred_soil, avatar, is_verified))
                row = cursor.fetchone()
                user_id = row["id"] if isinstance(row, dict) else row[0]
            conn.commit()
            return user_id, None
        except psycopg2.IntegrityError as e:
            conn.rollback()
            err_msg = str(e).lower()
            if "mobile" in err_msg:
                return None, "Mobile number is already registered."
            elif "email" in err_msg:
                return None, "Email address is already registered."
            return None, "A user with this mobile or email already exists."
        finally:
            conn.close()

    # SQLite Mode
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO users (name, mobile, email, password_hash, farm_location, land_area, land_unit, preferred_soil, avatar, is_verified)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (name_clean, mobile_clean, email_clean, password_hash, farm_clean, area_val, land_unit, preferred_soil, avatar, is_verified))
        conn.commit()
        user_id = cursor.lastrowid
        return user_id, None
    except sqlite3.IntegrityError as e:
        err_msg = str(e).lower()
        if "mobile" in err_msg:
            return None, "Mobile number is already registered."
        elif "email" in err_msg:
            return None, "Email address is already registered."
        return None, "A user with this mobile or email already exists."
    finally:
        conn.close()


def delete_unverified_user(email, mobile=None):
    email_clean = email.strip().lower()
    mobile_clean = str(mobile).strip() if mobile else None

    if is_postgres():
        conn = get_pg_connection()
        try:
            with conn.cursor() as cursor:
                if mobile_clean:
                    cursor.execute("DELETE FROM users WHERE (LOWER(email) = LOWER(%s) OR mobile = %s) AND is_verified = 0", (email_clean, mobile_clean))
                else:
                    cursor.execute("DELETE FROM users WHERE LOWER(email) = LOWER(%s) AND is_verified = 0", (email_clean,))
            conn.commit()
        finally:
            conn.close()
        return

    # SQLite Mode
    conn = get_db()
    cursor = conn.cursor()
    if mobile_clean:
        cursor.execute("DELETE FROM users WHERE (LOWER(email) = LOWER(?) OR mobile = ?) AND is_verified = 0", (email_clean, mobile_clean))
    else:
        cursor.execute("DELETE FROM users WHERE LOWER(email) = LOWER(?) AND is_verified = 0", (email_clean,))
    conn.commit()
    conn.close()


def update_user_otp(user_id, otp_hash, expiry_timestamp, sent_at=None):
    sent_time = sent_at or time.time()
    if is_postgres():
        conn = get_pg_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    UPDATE users
                    SET otp_hash = %s, otp_expiry = %s, otp_attempts = 0, otp_sent_at = %s
                    WHERE id = %s
                """, (otp_hash, expiry_timestamp, sent_time, user_id))
            conn.commit()
        finally:
            conn.close()
        return

    # SQLite Mode
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE users
        SET otp_hash = ?, otp_expiry = ?, otp_attempts = 0, otp_sent_at = ?
        WHERE id = ?
    """, (otp_hash, expiry_timestamp, sent_time, user_id))
    conn.commit()
    conn.close()


def get_user_otp_state(user_id):
    if is_postgres():
        conn = get_pg_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT otp_hash, otp_expiry, otp_attempts, otp_sent_at
                    FROM users WHERE id = %s AND is_verified = 0
                """, (user_id,))
                row = cursor.fetchone()
                return dict(row) if row else None
        finally:
            conn.close()

    # SQLite Mode
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT otp_hash, otp_expiry, otp_attempts, otp_sent_at
        FROM users WHERE id = ? AND is_verified = 0
    """, (user_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def verify_user_otp(email, entered_code):
    email_clean = email.strip().lower()
    code_clean = str(entered_code).strip()

    if is_postgres():
        conn = get_pg_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT id, otp_hash, otp_expiry, otp_attempts FROM users WHERE LOWER(email) = LOWER(%s) AND is_verified = 0
                """, (email_clean,))
                user = cursor.fetchone()

                if not user:
                    return False, "User not found."

                saved_code = user["otp_hash"]
                expiry = user["otp_expiry"]
                attempts = user["otp_attempts"] or 0

                if not saved_code or not expiry:
                    return False, "No active OTP found. Please request a new OTP."

                if time.time() > expiry:
                    cursor.execute("UPDATE users SET otp_hash = NULL, otp_expiry = NULL, otp_attempts = 0, otp_sent_at = NULL WHERE id = %s", (user["id"],))
                    conn.commit()
                    return False, "OTP has expired. Please request a new OTP."

                if attempts >= 5:
                    return False, "Too many invalid attempts. Please request a new OTP."

                if check_password_hash(saved_code, code_clean):
                    cursor.execute("""
                        UPDATE users
                        SET is_verified = 1, otp_hash = NULL, otp_expiry = NULL, otp_attempts = 0, otp_sent_at = NULL
                        WHERE id = %s
                    """, (user["id"],))
                    conn.commit()
                    return True, user["id"]
                else:
                    attempts += 1
                    cursor.execute("UPDATE users SET otp_attempts = %s WHERE id = %s", (attempts, user["id"]))
                    conn.commit()
                    if attempts >= 5:
                        return False, "Too many invalid attempts. Please request a new OTP."
                    return False, "Invalid OTP. Please try again."
        finally:
            conn.close()

    # SQLite Mode
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, otp_hash, otp_expiry, otp_attempts FROM users WHERE LOWER(email) = LOWER(?) AND is_verified = 0
    """, (email_clean,))
    user = cursor.fetchone()

    if not user:
        conn.close()
        return False, "User not found."

    saved_code = user["otp_hash"]
    expiry = user["otp_expiry"]
    attempts = user["otp_attempts"] or 0

    if not saved_code or not expiry:
        conn.close()
        return False, "No active OTP found. Please request a new OTP."

    if time.time() > expiry:
        cursor.execute("UPDATE users SET otp_hash = NULL, otp_expiry = NULL, otp_attempts = 0, otp_sent_at = NULL WHERE id = ?", (user["id"],))
        conn.commit()
        conn.close()
        return False, "OTP has expired. Please request a new OTP."

    if attempts >= 5:
        conn.close()
        return False, "Too many invalid attempts. Please request a new OTP."

    if check_password_hash(saved_code, code_clean):
        cursor.execute("""
            UPDATE users
            SET is_verified = 1, otp_hash = NULL, otp_expiry = NULL, otp_attempts = 0, otp_sent_at = NULL
            WHERE id = ?
        """, (user["id"],))
        conn.commit()
        conn.close()
        return True, user["id"]
    else:
        attempts += 1
        cursor.execute("UPDATE users SET otp_attempts = ? WHERE id = ?", (attempts, user["id"]))
        conn.commit()
        conn.close()
        if attempts >= 5:
            return False, "Too many invalid attempts. Please request a new OTP."
        return False, "Invalid OTP. Please try again."


def authenticate_user(login_identifier, password):
    ident_clean = login_identifier.strip()
    ident_lower = ident_clean.lower()

    if is_postgres():
        conn = get_pg_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT * FROM users WHERE LOWER(email) = LOWER(%s) OR mobile = %s
                """, (ident_lower, ident_clean))
                user = cursor.fetchone()
                if user and check_password_hash(user["password_hash"], password):
                    return dict(user)
                return None
        finally:
            conn.close()

    # SQLite Mode
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM users WHERE LOWER(email) = LOWER(?) OR mobile = ?
    """, (ident_lower, ident_clean))
    user = cursor.fetchone()
    conn.close()

    if user and check_password_hash(user["password_hash"], password):
        return dict(user)
    return None


def get_user_by_id(user_id):
    if is_postgres():
        conn = get_pg_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
                user = cursor.fetchone()
                return dict(user) if user else None
        finally:
            conn.close()

    # SQLite Mode
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()
    return dict(user) if user else None


def get_user_by_email(email):
    email_clean = email.strip().lower()
    if is_postgres():
        conn = get_pg_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM users WHERE LOWER(email) = LOWER(%s)", (email_clean,))
                user = cursor.fetchone()
                return dict(user) if user else None
        finally:
            conn.close()

    # SQLite Mode
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE LOWER(email) = LOWER(?)", (email_clean,))
    user = cursor.fetchone()
    conn.close()
    return dict(user) if user else None


def verify_reset_otp(email, entered_code):
    email_clean = email.strip().lower()
    code_clean = str(entered_code).strip()

    if is_postgres():
        conn = get_pg_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT id, otp_hash, otp_expiry, otp_attempts FROM users WHERE LOWER(email) = LOWER(%s)
                """, (email_clean,))
                user = cursor.fetchone()

                if not user:
                    return False, "User not found."

                saved_code = user["otp_hash"]
                expiry = user["otp_expiry"]
                attempts = user["otp_attempts"] or 0

                if not saved_code or not expiry:
                    return False, "No active OTP found. Please request a new OTP."

                if time.time() > expiry:
                    cursor.execute("UPDATE users SET otp_hash = NULL, otp_expiry = NULL, otp_attempts = 0, otp_sent_at = NULL WHERE id = %s", (user["id"],))
                    conn.commit()
                    return False, "OTP has expired. Please request a new OTP."

                if attempts >= 5:
                    return False, "Too many invalid attempts. Please request a new OTP."

                if check_password_hash(saved_code, code_clean):
                    cursor.execute("""
                        UPDATE users
                        SET otp_hash = NULL, otp_expiry = NULL, otp_attempts = 0, otp_sent_at = NULL
                        WHERE id = %s
                    """, (user["id"],))
                    conn.commit()
                    return True, user["id"]
                else:
                    attempts += 1
                    cursor.execute("UPDATE users SET otp_attempts = %s WHERE id = %s", (attempts, user["id"]))
                    conn.commit()
                    if attempts >= 5:
                        return False, "Too many invalid attempts. Please request a new OTP."
                    return False, "Invalid OTP. Please try again."
        finally:
            conn.close()

    # SQLite Mode
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, otp_hash, otp_expiry, otp_attempts FROM users WHERE LOWER(email) = LOWER(?)
    """, (email_clean,))
    user = cursor.fetchone()

    if not user:
        conn.close()
        return False, "User not found."

    saved_code = user["otp_hash"]
    expiry = user["otp_expiry"]
    attempts = user["otp_attempts"] or 0

    if not saved_code or not expiry:
        conn.close()
        return False, "No active OTP found. Please request a new OTP."

    if time.time() > expiry:
        cursor.execute("UPDATE users SET otp_hash = NULL, otp_expiry = NULL, otp_attempts = 0, otp_sent_at = NULL WHERE id = ?", (user["id"],))
        conn.commit()
        conn.close()
        return False, "OTP has expired. Please request a new OTP."

    if attempts >= 5:
        conn.close()
        return False, "Too many invalid attempts. Please request a new OTP."

    if check_password_hash(saved_code, code_clean):
        cursor.execute("""
            UPDATE users
            SET otp_hash = NULL, otp_expiry = NULL, otp_attempts = 0, otp_sent_at = NULL
            WHERE id = ?
        """, (user["id"],))
        conn.commit()
        conn.close()
        return True, user["id"]
    else:
        attempts += 1
        cursor.execute("UPDATE users SET otp_attempts = ? WHERE id = ?", (attempts, user["id"]))
        conn.commit()
        conn.close()
        if attempts >= 5:
            return False, "Too many invalid attempts. Please request a new OTP."
        return False, "Invalid OTP. Please try again."


def update_user_password(user_id, new_password):
    password_hash = generate_password_hash(new_password)

    if is_postgres():
        conn = get_pg_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("UPDATE users SET password_hash = %s WHERE id = %s", (password_hash, user_id))
                success = cursor.rowcount > 0
            conn.commit()
            return success
        finally:
            conn.close()

    # SQLite Mode
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET password_hash = ? WHERE id = ?", (password_hash, user_id))
    conn.commit()
    success = cursor.rowcount > 0
    conn.close()
    return success


def update_user_profile(user_id, name, mobile, email, farm_location, land_area, land_unit, preferred_soil, avatar):
    name_clean = name.strip()
    mobile_clean = mobile.strip()
    email_clean = email.strip().lower()
    farm_clean = farm_location.strip()
    area_val = float(land_area)

    if is_postgres():
        import psycopg2
        conn = get_pg_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    UPDATE users
                    SET name = %s, mobile = %s, email = %s, farm_location = %s, land_area = %s, land_unit = %s, preferred_soil = %s, avatar = %s
                    WHERE id = %s
                """, (name_clean, mobile_clean, email_clean, farm_clean, area_val, land_unit, preferred_soil, avatar, user_id))
                success = cursor.rowcount > 0
            conn.commit()
            return True, None
        except psycopg2.IntegrityError:
            conn.rollback()
            return False, "Mobile or Email already in use by another account."
        finally:
            conn.close()

    # SQLite Mode
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE users
            SET name = ?, mobile = ?, email = ?, farm_location = ?, land_area = ?, land_unit = ?, preferred_soil = ?, avatar = ?
            WHERE id = ?
        """, (name_clean, mobile_clean, email_clean, farm_clean, area_val, land_unit, preferred_soil, avatar, user_id))
        conn.commit()
        return True, None
    except sqlite3.IntegrityError:
        return False, "Mobile or Email already in use by another account."
    finally:
        conn.close()


# -------------------------------------------------------------
# RECOMMENDATIONS LOGGING
# -------------------------------------------------------------

def save_recommendation(user_id, soil_type, ph, temperature, humidity, rainfall, recommended_crop, alternative_crops, decision_notes="", variety="Standard"):
    alt_json = json.dumps(alternative_crops) if isinstance(alternative_crops, list) else str(alternative_crops)
    soil_clean = soil_type.strip()
    ph_val = float(ph)
    temp_val = float(temperature)
    hum_val = float(humidity)
    rain_val = float(rainfall)

    if is_postgres():
        conn = get_pg_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO recommendations (user_id, soil_type, ph, temperature, humidity, rainfall, recommended_crop, variety, alternative_crops, decision_notes)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                """, (user_id, soil_clean, ph_val, temp_val, hum_val, rain_val, recommended_crop, variety, alt_json, decision_notes))
                row = cursor.fetchone()
                rec_id = row["id"] if isinstance(row, dict) else row[0]
            conn.commit()
            return rec_id
        finally:
            conn.close()

    # SQLite Mode
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO recommendations (user_id, soil_type, ph, temperature, humidity, rainfall, recommended_crop, variety, alternative_crops, decision_notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (user_id, soil_clean, ph_val, temp_val, hum_val, rain_val, recommended_crop, variety, alt_json, decision_notes))
    conn.commit()
    rec_id = cursor.lastrowid
    conn.close()
    return rec_id


def get_recommendation_history(user_id, limit=50):
    if is_postgres():
        conn = get_pg_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT * FROM recommendations
                    WHERE user_id = %s
                    ORDER BY created_at DESC
                    LIMIT %s
                """, (user_id, limit))
                rows = cursor.fetchall()
                results = []
                for r in rows:
                    item = dict(r)
                    try:
                        item["alternative_crops_list"] = json.loads(item["alternative_crops"])
                    except Exception:
                        item["alternative_crops_list"] = []
                    if "variety" not in item or not item["variety"]:
                        item["variety"] = "Standard"
                    results.append(item)
                return results
        finally:
            conn.close()

    # SQLite Mode
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM recommendations
        WHERE user_id = ?
        ORDER BY created_at DESC
        LIMIT ?
    """, (user_id, limit))
    rows = cursor.fetchall()
    conn.close()

    results = []
    for r in rows:
        item = dict(r)
        try:
            item["alternative_crops_list"] = json.loads(item["alternative_crops"])
        except Exception:
            item["alternative_crops_list"] = []
        if "variety" not in item or not item["variety"]:
            item["variety"] = "Standard"
        results.append(item)
    return results


def get_recommendation_by_id(rec_id, user_id=None):
    if is_postgres():
        conn = get_pg_connection()
        try:
            with conn.cursor() as cursor:
                if user_id:
                    cursor.execute("SELECT * FROM recommendations WHERE id = %s AND user_id = %s", (rec_id, user_id))
                else:
                    cursor.execute("SELECT * FROM recommendations WHERE id = %s", (rec_id,))
                row = cursor.fetchone()
                if not row:
                    return None
                item = dict(row)
                try:
                    item["alternative_crops_list"] = json.loads(item["alternative_crops"])
                except Exception:
                    item["alternative_crops_list"] = []
                if "variety" not in item or not item["variety"]:
                    item["variety"] = "Standard"
                return item
        finally:
            conn.close()

    # SQLite Mode
    conn = get_db()
    cursor = conn.cursor()
    if user_id:
        cursor.execute("SELECT * FROM recommendations WHERE id = ? AND user_id = ?", (rec_id, user_id))
    else:
        cursor.execute("SELECT * FROM recommendations WHERE id = ?", (rec_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        return None
    item = dict(row)
    try:
        item["alternative_crops_list"] = json.loads(item["alternative_crops"])
    except Exception:
        item["alternative_crops_list"] = []
    if "variety" not in item or not item["variety"]:
        item["variety"] = "Standard"
    return item


def delete_recommendation(rec_id, user_id):
    if is_postgres():
        conn = get_pg_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("DELETE FROM recommendations WHERE id = %s AND user_id = %s", (rec_id, user_id))
                deleted = cursor.rowcount > 0
            conn.commit()
            return deleted
        finally:
            conn.close()

    # SQLite Mode
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM recommendations WHERE id = ? AND user_id = ?", (rec_id, user_id))
    conn.commit()
    deleted = cursor.rowcount > 0
    conn.close()
    return deleted


# -------------------------------------------------------------
# EXPENSES MANAGEMENT
# -------------------------------------------------------------

def add_expense(user_id, expense_date, category, amount, description=""):
    amt_val = float(amount)
    desc_clean = description.strip()

    if is_postgres():
        conn = get_pg_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO expenses (user_id, expense_date, category, amount, description)
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING id
                """, (user_id, expense_date, category, amt_val, desc_clean))
                row = cursor.fetchone()
                exp_id = row["id"] if isinstance(row, dict) else row[0]
            conn.commit()
            return exp_id
        finally:
            conn.close()

    # SQLite Mode
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO expenses (user_id, expense_date, category, amount, description)
        VALUES (?, ?, ?, ?, ?)
    """, (user_id, expense_date, category, amt_val, desc_clean))
    conn.commit()
    exp_id = cursor.lastrowid
    conn.close()
    return exp_id


def get_user_expenses(user_id):
    if is_postgres():
        conn = get_pg_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT * FROM expenses
                    WHERE user_id = %s
                    ORDER BY expense_date DESC, created_at DESC
                """, (user_id,))
                rows = cursor.fetchall()
                return [dict(r) for r in rows]
        finally:
            conn.close()

    # SQLite Mode
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM expenses
        WHERE user_id = ?
        ORDER BY expense_date DESC, created_at DESC
    """, (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_expense_summary(user_id):
    if is_postgres():
        conn = get_pg_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT category, SUM(amount) as total_amount, COUNT(*) as count
                    FROM expenses
                    WHERE user_id = %s
                    GROUP BY category
                """, (user_id,))
                category_rows = cursor.fetchall()

                cursor.execute("""
                    SELECT SUM(amount) as total_expenses, COUNT(*) as total_count
                    FROM expenses
                    WHERE user_id = %s
                """, (user_id,))
                total_row = cursor.fetchone()

                by_category = {r["category"]: float(r["total_amount"]) for r in category_rows}
                total_sum = float(total_row["total_expenses"]) if total_row and total_row["total_expenses"] else 0.0
                total_cnt = total_row["total_count"] if total_row and total_row["total_count"] else 0

                return {
                    "by_category": by_category,
                    "total_expenses": total_sum,
                    "total_count": total_cnt
                }
        finally:
            conn.close()

    # SQLite Mode
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT category, SUM(amount) as total_amount, COUNT(*) as count
        FROM expenses
        WHERE user_id = ?
        GROUP BY category
    """, (user_id,))
    category_rows = cursor.fetchall()

    cursor.execute("""
        SELECT SUM(amount) as total_expenses, COUNT(*) as total_count
        FROM expenses
        WHERE user_id = ?
    """, (user_id,))
    total_row = cursor.fetchone()
    conn.close()

    by_category = {r["category"]: float(r["total_amount"]) for r in category_rows}
    total_sum = float(total_row["total_expenses"]) if total_row and total_row["total_expenses"] else 0.0

    return {
        "by_category": by_category,
        "total_expenses": total_sum,
        "total_count": total_row["total_count"] if total_row and total_row["total_count"] else 0
    }


def delete_expense(expense_id, user_id):
    if is_postgres():
        conn = get_pg_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("DELETE FROM expenses WHERE id = %s AND user_id = %s", (expense_id, user_id))
                deleted = cursor.rowcount > 0
            conn.commit()
            return deleted
        finally:
            conn.close()

    # SQLite Mode
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM expenses WHERE id = ? AND user_id = ?", (expense_id, user_id))
    conn.commit()
    deleted = cursor.rowcount > 0
    conn.close()
    return deleted


# -------------------------------------------------------------
# FARM NOTES MANAGEMENT
# -------------------------------------------------------------

def add_note(user_id, title, content, tag="General"):
    title_clean = title.strip()
    content_clean = content.strip()
    tag_clean = tag.strip()

    if is_postgres():
        conn = get_pg_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO notes (user_id, title, content, tag)
                    VALUES (%s, %s, %s, %s)
                    RETURNING id
                """, (user_id, title_clean, content_clean, tag_clean))
                row = cursor.fetchone()
                note_id = row["id"] if isinstance(row, dict) else row[0]
            conn.commit()
            return note_id
        finally:
            conn.close()

    # SQLite Mode
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO notes (user_id, title, content, tag)
        VALUES (?, ?, ?, ?)
    """, (user_id, title_clean, content_clean, tag_clean))
    conn.commit()
    note_id = cursor.lastrowid
    conn.close()
    return note_id


def get_user_notes(user_id):
    if is_postgres():
        conn = get_pg_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT * FROM notes
                    WHERE user_id = %s
                    ORDER BY updated_at DESC
                """, (user_id,))
                rows = cursor.fetchall()
                return [dict(r) for r in rows]
        finally:
            conn.close()

    # SQLite Mode
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM notes
        WHERE user_id = ?
        ORDER BY updated_at DESC
    """, (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def delete_note(note_id, user_id):
    if is_postgres():
        conn = get_pg_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("DELETE FROM notes WHERE id = %s AND user_id = %s", (note_id, user_id))
                deleted = cursor.rowcount > 0
            conn.commit()
            return deleted
        finally:
            conn.close()

    # SQLite Mode
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM notes WHERE id = ? AND user_id = ?", (note_id, user_id))
    conn.commit()
    deleted = cursor.rowcount > 0
    conn.close()
    return deleted


# -------------------------------------------------------------
# FARM REMINDERS MANAGEMENT
# -------------------------------------------------------------

def add_reminder(user_id, title, reminder_date, reminder_time="00:00", description="", crop="", variety="", category="General"):
    title_clean = title.strip()
    desc_clean = description.strip()
    crop_clean = crop.strip()
    variety_clean = variety.strip()
    cat_clean = category.strip()

    if is_postgres():
        conn = get_pg_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO reminders (user_id, title, reminder_date, reminder_time, description, crop, variety, category, is_completed)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 0)
                    RETURNING id
                """, (user_id, title_clean, reminder_date, reminder_time, desc_clean, crop_clean, variety_clean, cat_clean))
                row = cursor.fetchone()
                rem_id = row["id"] if isinstance(row, dict) else row[0]
            conn.commit()
            return rem_id
        finally:
            conn.close()

    # SQLite Mode
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO reminders (user_id, title, reminder_date, reminder_time, description, crop, variety, category, is_completed)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0)
    """, (user_id, title_clean, reminder_date, reminder_time, desc_clean, crop_clean, variety_clean, cat_clean))
    conn.commit()
    rem_id = cursor.lastrowid
    conn.close()
    return rem_id


def get_user_reminders(user_id, limit=50):
    if is_postgres():
        conn = get_pg_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT * FROM reminders
                    WHERE user_id = %s
                    ORDER BY reminder_date ASC, reminder_time ASC, created_at DESC
                    LIMIT %s
                """, (user_id, limit))
                rows = cursor.fetchall()
                return [dict(r) for r in rows]
        finally:
            conn.close()

    # SQLite Mode
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM reminders
        WHERE user_id = ?
        ORDER BY reminder_date ASC, reminder_time ASC, created_at DESC
        LIMIT ?
    """, (user_id, limit))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_upcoming_reminders(user_id, limit=5):
    if is_postgres():
        conn = get_pg_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT * FROM reminders
                    WHERE user_id = %s AND is_completed = 0
                    ORDER BY reminder_date ASC, reminder_time ASC
                    LIMIT %s
                """, (user_id, limit))
                rows = cursor.fetchall()
                return [dict(r) for r in rows]
        finally:
            conn.close()

    # SQLite Mode
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM reminders
        WHERE user_id = ? AND is_completed = 0
        ORDER BY reminder_date ASC, reminder_time ASC
        LIMIT ?
    """, (user_id, limit))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def toggle_reminder(reminder_id, user_id):
    if is_postgres():
        conn = get_pg_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    UPDATE reminders
                    SET is_completed = CASE WHEN is_completed = 1 THEN 0 ELSE 1 END
                    WHERE id = %s AND user_id = %s
                """, (reminder_id, user_id))
                success = cursor.rowcount > 0
            conn.commit()
            return success
        finally:
            conn.close()

    # SQLite Mode
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE reminders
        SET is_completed = CASE WHEN is_completed = 1 THEN 0 ELSE 1 END
        WHERE id = ? AND user_id = ?
    """, (reminder_id, user_id))
    conn.commit()
    success = cursor.rowcount > 0
    conn.close()
    return success


def delete_reminder(reminder_id, user_id):
    if is_postgres():
        conn = get_pg_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("DELETE FROM reminders WHERE id = %s AND user_id = %s", (reminder_id, user_id))
                deleted = cursor.rowcount > 0
            conn.commit()
            return deleted
        finally:
            conn.close()

    # SQLite Mode
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM reminders WHERE id = ? AND user_id = ?", (reminder_id, user_id))
    conn.commit()
    deleted = cursor.rowcount > 0
    conn.close()
    return deleted


if __name__ == "__main__":
    init_db()
