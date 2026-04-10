import sqlite3
import pandas as pd
from datetime import datetime
from config.settings import DB_PATH


def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            topic TEXT NOT NULL,
            target_duration INTEGER,
            actual_duration INTEGER,
            focus_score REAL,
            notes TEXT,
            started_at TIMESTAMP,
            ended_at TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS distractions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER,
            distraction_type TEXT,
            description TEXT,
            logged_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (session_id) REFERENCES sessions(id)
        )
    """)
    conn.commit()
    conn.close()


def create_user(name: str) -> int:
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO users (name) VALUES (?)", (name,))
    user_id = c.lastrowid
    conn.commit()
    conn.close()
    return user_id


def start_session(user_id: int, topic: str, target_duration: int) -> int:
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "INSERT INTO sessions (user_id, topic, target_duration, started_at) VALUES (?,?,?,?)",
        (user_id, topic, target_duration, datetime.now())
    )
    session_id = c.lastrowid
    conn.commit()
    conn.close()
    return session_id


def calculate_focus_score(session_id: int, actual_duration: int, target_duration: int) -> float:
    """
    Focus score (0-10) berdasarkan:
    - Completion rate: durasi aktual vs target (bobot 40%)
    - Distraction rate: jumlah distraksi per jam (bobot 60%)
    """
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM distractions WHERE session_id=?", (session_id,))
    distraction_count = c.fetchone()[0]
    conn.close()

    completion_ratio = min(actual_duration / target_duration, 1.0) if target_duration > 0 else 1.0
    completion_score = completion_ratio * 10

    hours = max(actual_duration / 60, 1/60)
    distraction_rate = distraction_count / hours
    distraction_score = max(0, 10 - (distraction_rate / 4))

    focus_score = (completion_score * 0.4) + (distraction_score * 0.6)
    return round(min(focus_score, 10.0), 1)


def end_session(session_id: int, actual_duration: int, target_duration: int, notes: str = "") -> float:
    focus_score = calculate_focus_score(session_id, actual_duration, target_duration)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "UPDATE sessions SET actual_duration=?, focus_score=?, notes=?, ended_at=? WHERE id=?",
        (actual_duration, focus_score, notes, datetime.now(), session_id)
    )
    conn.commit()
    conn.close()
    return focus_score


def log_distraction(session_id: int, distraction_type: str, description: str = ""):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "INSERT INTO distractions (session_id, distraction_type, description) VALUES (?,?,?)",
        (session_id, distraction_type, description)
    )
    conn.commit()
    conn.close()


def get_user_sessions(user_id: int) -> pd.DataFrame:
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(
        "SELECT * FROM sessions WHERE user_id=? ORDER BY started_at DESC",
        conn, params=(user_id,)
    )
    conn.close()
    return df


def get_session_distractions(session_id: int) -> pd.DataFrame:
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(
        "SELECT * FROM distractions WHERE session_id=? ORDER BY logged_at",
        conn, params=(session_id,)
    )
    conn.close()
    return df