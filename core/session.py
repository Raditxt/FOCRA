import sqlite3
import pandas as pd
from datetime import datetime, timezone
from config.settings import DB_PATH


def _get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_db():
    with _get_connection() as conn:
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                id               INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id          INTEGER NOT NULL,
                topic            TEXT NOT NULL,
                target_duration  INTEGER NOT NULL,
                actual_duration  INTEGER,
                focus_score      REAL,
                notes            TEXT,
                started_at       TIMESTAMP NOT NULL,
                ended_at         TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE RESTRICT
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS distractions (
                id               INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id       INTEGER NOT NULL,
                distraction_type TEXT NOT NULL,
                description      TEXT DEFAULT '',
                elapsed_minutes  INTEGER,
                logged_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS daily_context (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id       INTEGER NOT NULL,
                session_id    INTEGER NOT NULL,
                energy_level  INTEGER CHECK(energy_level BETWEEN 1 AND 5),
                environment   TEXT,
                logged_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id)    REFERENCES users(id) ON DELETE RESTRICT,
                FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE
            )
        """)
        conn.commit()


def create_user(name: str) -> int:
    normalized = name.strip().lower()
    with _get_connection() as conn:
        c = conn.cursor()
        c.execute("INSERT OR IGNORE INTO users (name) VALUES (?)", (normalized,))
        conn.commit()
        c.execute("SELECT id FROM users WHERE name = ?", (normalized,))
        return c.fetchone()[0]


def start_session(user_id: int, topic: str, target_duration: int) -> int:
    if target_duration <= 0:
        raise ValueError("target_duration must be positive")
    with _get_connection() as conn:
        c = conn.cursor()
        c.execute(
            "INSERT INTO sessions (user_id, topic, target_duration, started_at) VALUES (?,?,?,?)",
            (user_id, topic, target_duration, datetime.now(timezone.utc))
        )
        session_id = c.lastrowid
        conn.commit()
    return session_id


def log_daily_context(user_id: int, session_id: int, energy_level: int, environment: str):
    with _get_connection() as conn:
        c = conn.cursor()
        c.execute(
            """INSERT INTO daily_context (user_id, session_id, energy_level, environment)
               VALUES (?,?,?,?)""",
            (user_id, session_id, energy_level, environment)
        )
        conn.commit()


def log_distraction(session_id: int, distraction_type: str,
                    elapsed_minutes: int = 0, description: str = ""):
    with _get_connection() as conn:
        c = conn.cursor()
        c.execute("SELECT ended_at FROM sessions WHERE id = ?", (session_id,))
        row = c.fetchone()
        if row is None:
            raise ValueError(f"Session {session_id} not found")
        if row[0] is not None:
            raise RuntimeError(f"Cannot log distraction to ended session {session_id}")
        c.execute(
            """INSERT INTO distractions
               (session_id, distraction_type, description, elapsed_minutes)
               VALUES (?,?,?,?)""",
            (session_id, distraction_type, description, elapsed_minutes)
        )
        conn.commit()


def calculate_focus_score(session_id: int, actual_duration: int) -> float:
    if actual_duration <= 0:
        raise ValueError("actual_duration must be positive")
    with _get_connection() as conn:
        c = conn.cursor()
        c.execute("SELECT target_duration FROM sessions WHERE id = ?", (session_id,))
        row = c.fetchone()
        if row is None:
            raise ValueError(f"Session {session_id} not found")
        target_duration = row[0]
        c.execute("SELECT COUNT(*) FROM distractions WHERE session_id = ?", (session_id,))
        distraction_count = c.fetchone()[0]

    completion_ratio = min(actual_duration / target_duration, 1.0) if target_duration > 0 else 1.0
    completion_score = completion_ratio * 10
    hours = max(actual_duration / 60, 1/60)
    distraction_rate = distraction_count / hours
    distraction_score = max(0, 10 - (distraction_rate / 4))
    return round(min((completion_score * 0.4) + (distraction_score * 0.6), 10.0), 1)


def end_session(session_id: int, actual_duration: int, notes: str = "") -> float:
    if actual_duration <= 0:
        raise ValueError("actual_duration must be positive")
    with _get_connection() as conn:
        c = conn.cursor()
        c.execute("SELECT ended_at FROM sessions WHERE id = ?", (session_id,))
        row = c.fetchone()
        if row is None:
            raise ValueError(f"Session {session_id} not found")
        if row[0] is not None:
            raise RuntimeError(f"Session {session_id} already ended")

    focus_score = calculate_focus_score(session_id, actual_duration)

    with _get_connection() as conn:
        c = conn.cursor()
        c.execute(
            """UPDATE sessions
               SET actual_duration=?, focus_score=?, notes=?, ended_at=?
               WHERE id=?""",
            (actual_duration, focus_score, notes, datetime.now(timezone.utc), session_id)
        )
        conn.commit()
    return focus_score


def get_user_sessions(user_id: int) -> pd.DataFrame:
    with _get_connection() as conn:
        df = pd.read_sql_query(
            "SELECT * FROM sessions WHERE user_id=? ORDER BY started_at DESC",
            conn, params=(user_id,)
        )
    return df


def get_session_distractions(session_id: int) -> pd.DataFrame:
    with _get_connection() as conn:
        df = pd.read_sql_query(
            "SELECT * FROM distractions WHERE session_id=? ORDER BY logged_at",
            conn, params=(session_id,)
        )
    return df


def get_distraction_timeline(user_id: int) -> pd.DataFrame:
    with _get_connection() as conn:
        df = pd.read_sql_query(
            """SELECT d.distraction_type, d.elapsed_minutes, d.logged_at,
                      s.topic, s.target_duration
               FROM distractions d
               JOIN sessions s ON d.session_id = s.id
               WHERE s.user_id = ?
               ORDER BY d.logged_at DESC""",
            conn, params=(user_id,)
        )
    return df


def get_user_context_history(user_id: int) -> pd.DataFrame:
    with _get_connection() as conn:
        df = pd.read_sql_query(
            """SELECT dc.energy_level, dc.environment, s.focus_score,
                      s.topic, s.actual_duration, s.target_duration
               FROM daily_context dc
               JOIN sessions s ON dc.session_id = s.id
               WHERE dc.user_id = ?
               ORDER BY dc.logged_at DESC""",
            conn, params=(user_id,)
        )
    return df