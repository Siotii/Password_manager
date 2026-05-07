import hashlib
import hmac
import os
import sqlite3
from pathlib import Path

from cryptography.fernet import Fernet, InvalidToken

BASE_DIR = Path(__file__).resolve().parent
DB_NAME = BASE_DIR / "padflock.db"
KEY_FILE = BASE_DIR / ".padflock.key"
HASH_ITERATIONS = 100_000


def load_key():
    if KEY_FILE.exists():
        return KEY_FILE.read_bytes()

    key = Fernet.generate_key()
    KEY_FILE.write_bytes(key)
    return key


cipher = Fernet(load_key())


def connect():
    return sqlite3.connect(DB_NAME)


def init_db():
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        salt TEXT NOT NULL,
        password TEXT NOT NULL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS vault (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        site TEXT NOT NULL,
        username TEXT NOT NULL,
        password TEXT NOT NULL,
        password_hash TEXT,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
    """)

    cursor.execute("PRAGMA table_info(vault)")
    columns = {column[1] for column in cursor.fetchall()}
    if "password_hash" not in columns:
        cursor.execute("ALTER TABLE vault ADD COLUMN password_hash TEXT")

    conn.commit()
    conn.close()


def generate_salt():
    return os.urandom(16).hex()


def hash_password(password, salt):
    return hashlib.pbkdf2_hmac(
        "sha256",
        password.encode(),
        bytes.fromhex(salt),
        HASH_ITERATIONS
    ).hex()


def hash_vault_password(password):
    return hmac.new(load_key(), password.encode(), hashlib.sha256).hexdigest()


def register_user(username, password):
    username = username.strip()
    if not username or not password:
        return False

    conn = connect()
    cursor = conn.cursor()

    salt = generate_salt()
    hashed = hash_password(password, salt)

    try:
        cursor.execute(
            "INSERT INTO users (username, salt, password) VALUES (?, ?, ?)",
            (username, salt, hashed)
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()


def login_user(username, password):
    username = username.strip()
    conn = connect()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id, salt, password FROM users WHERE username=?",
        (username,)
    )

    result = cursor.fetchone()
    conn.close()

    if result is None:
        return None

    user_id, salt, stored_hash = result
    entered_hash = hash_password(password, salt)

    if hmac.compare_digest(entered_hash, stored_hash):
        return user_id
    return None



def encrypt_password(password):
    return cipher.encrypt(password.encode()).decode()


def decrypt_password(password):
    try:
        return cipher.decrypt(password.encode()).decode()
    except InvalidToken:
        return "[Unable to decrypt: key changed]"



def save_password(user_id, site, username, password):
    site = site.strip()
    username = username.strip()
    if not site or not username or not password:
        raise ValueError("Site, username, and password are required.")

    conn = connect()
    cursor = conn.cursor()

    encrypted = encrypt_password(password)
    password_hash = hash_vault_password(password)

    cursor.execute(
        """
        INSERT INTO vault (user_id, site, username, password, password_hash)
        VALUES (?, ?, ?, ?, ?)
        """,
        (user_id, site, username, encrypted, password_hash)
    )

    conn.commit()
    conn.close()


def get_passwords(user_id):
    conn = connect()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT site, username, password FROM vault WHERE user_id=? ORDER BY site COLLATE NOCASE",
        (user_id,)
    )

    data = cursor.fetchall()
    conn.close()

    return [
        (site, user, decrypt_password(pw))
        for site, user, pw in data
    ]


def is_duplicate(user_id, password):
    conn = connect()
    cursor = conn.cursor()

    password_hash = hash_vault_password(password)
    cursor.execute(
        "SELECT 1 FROM vault WHERE user_id=? AND password_hash=? LIMIT 1",
        (user_id, password_hash)
    )

    match = cursor.fetchone()
    conn.close()

    return match is not None
