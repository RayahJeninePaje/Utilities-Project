
import sqlite3
import hashlib
import os
import hmac

DATABASE_NAME = "datagen.db"


def connect_db():
    return sqlite3.connect(DATABASE_NAME)


def create_tables():
    connection = connect_db()
    cursor = connection.cursor()

    # User accounts table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            salt TEXT NOT NULL
        )
    """)

    # Generated fake records table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            full_name TEXT,
            address TEXT,
            birthdate TEXT,
            mobile_number TEXT,
            email TEXT,
            gender TEXT,
            username TEXT,
            city TEXT,
            occupation TEXT,
            postal_code TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    connection.commit()
    connection.close()


def hash_password(password, salt):
    return hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        600000
    ).hex()


def register_user(username, password):
    connection = connect_db()
    cursor = connection.cursor()

    salt = os.urandom(16)
    password_hash = hash_password(password, salt)

    try:
        cursor.execute(
            "INSERT INTO users (username, password_hash, salt) VALUES (?, ?, ?)",
            (username, password_hash, salt.hex())
        )
        connection.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        connection.close()


def verify_user(username, password):
    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute(
        "SELECT id, password_hash, salt FROM users WHERE username = ?",
        (username,)
    )

    user = cursor.fetchone()
    connection.close()

    if user is None:
        return None

    user_id, stored_hash, stored_salt = user
    salt = bytes.fromhex(stored_salt)
    entered_hash = hash_password(password, salt)

    if hmac.compare_digest(entered_hash, stored_hash):
        return user_id

    return None


def save_record(user_id, record):
    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO records (
            user_id, full_name, address, birthdate,
            mobile_number, email, gender, username,
            city, occupation, postal_code
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        user_id,
        record["full_name"],
        record["address"],
        record["birthdate"],
        record["mobile_number"],
        record["email"],
        record["gender"],
        record["username"],
        record["city"],
        record["occupation"],
        record["postal_code"]
    ))

    connection.commit()
    connection.close()


def get_records(user_id):
    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute(
        "SELECT * FROM records WHERE user_id = ?",
        (user_id,)
    )

    records = cursor.fetchall()
    connection.close()

    return records
