from datetime import datetime, timezone
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from .config import get_settings

# SQLAlchemy is intentionally not an external dependency in this project.
# The application uses sqlite3 directly to keep installation small.
import sqlite3
from pathlib import Path
import json

settings = get_settings()
DB_PATH = Path("pocketsmart.db")

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    with get_connection() as conn:
        conn.executescript(
            '''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS recommendations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                planner_type TEXT NOT NULL,
                input_json TEXT NOT NULL,
                result_json TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
            );
            '''
        )
        conn.commit()

def create_user(name: str, email: str, password_hash: str) -> int:
    with get_connection() as conn:
        cur = conn.execute(
            "INSERT INTO users(name,email,password_hash,created_at) VALUES(?,?,?,?)",
            (name, email.lower().strip(), password_hash, datetime.now(timezone.utc).isoformat())
        )
        conn.commit()
        return cur.lastrowid

def get_user_by_email(email: str):
    with get_connection() as conn:
        return conn.execute("SELECT * FROM users WHERE email=?", (email.lower().strip(),)).fetchone()

def get_user_by_id(user_id: int):
    with get_connection() as conn:
        return conn.execute("SELECT * FROM users WHERE id=?", (user_id,)).fetchone()

def save_recommendation(user_id: int, planner_type: str, input_data: dict, result: dict) -> int:
    with get_connection() as conn:
        cur = conn.execute(
            "INSERT INTO recommendations(user_id,planner_type,input_json,result_json,created_at) VALUES(?,?,?,?,?)",
            (user_id, planner_type, json.dumps(input_data), json.dumps(result),
             datetime.now(timezone.utc).isoformat())
        )
        conn.commit()
        return cur.lastrowid

def get_history(user_id: int):
    with get_connection() as conn:
        return conn.execute(
            "SELECT id, planner_type, input_json, result_json, created_at "
            "FROM recommendations WHERE user_id=? ORDER BY id DESC",
            (user_id,)
        ).fetchall()

def get_recommendation(user_id: int, recommendation_id: int):
    with get_connection() as conn:
        return conn.execute(
            "SELECT * FROM recommendations WHERE id=? AND user_id=?",
            (recommendation_id, user_id)
        ).fetchone()
