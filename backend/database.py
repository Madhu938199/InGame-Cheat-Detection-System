"""
Database Access Layer & SQLite Management
Project: Multiplayer In-Game Cheat Detection System
File: backend/database.py
"""

import os
import sqlite3
import random
import string
from werkzeug.security import generate_password_hash

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'database', 'cheat_detection.db'))

def get_db():
    """Returns a thread-safe sqlite3 connection with dict-like row factory."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH, timeout=15)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    """Initializes tables and seeds default demonstration accounts and sample rooms."""
    conn = get_db()
    cur = conn.cursor()

    # Read and execute schema
    schema_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'database', 'schema.sql'))
    if os.path.exists(schema_path):
        with open(schema_path, 'r', encoding='utf-8') as f:
            cur.executescript(f.read())
    else:
        # Fallback inline schema creation
        cur.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                username VARCHAR(50) NOT NULL UNIQUE,
                password_hash VARCHAR(255) NOT NULL,
                role VARCHAR(20) NOT NULL DEFAULT 'player',
                avatar_color VARCHAR(20) DEFAULT '#6366f1',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS game_rooms (
                room_id INTEGER PRIMARY KEY AUTOINCREMENT,
                room_code VARCHAR(10) NOT NULL UNIQUE,
                room_name VARCHAR(100) NOT NULL,
                host_id INTEGER NOT NULL,
                status VARCHAR(20) NOT NULL DEFAULT 'waiting',
                min_players INTEGER NOT NULL DEFAULT 5,
                max_players INTEGER NOT NULL DEFAULT 10,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                started_at TIMESTAMP NULL,
                ended_at TIMESTAMP NULL,
                FOREIGN KEY (host_id) REFERENCES users(user_id) ON DELETE CASCADE
            );
            CREATE TABLE IF NOT EXISTS game_players (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                room_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                is_host INTEGER NOT NULL DEFAULT 0,
                is_bot INTEGER NOT NULL DEFAULT 0,
                player_status VARCHAR(20) NOT NULL DEFAULT 'ready',
                joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(room_id, user_id),
                FOREIGN KEY (room_id) REFERENCES game_rooms(room_id) ON DELETE CASCADE,
                FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
            );
            CREATE TABLE IF NOT EXISTS gameplay_stats (
                stat_id INTEGER PRIMARY KEY AUTOINCREMENT,
                room_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                kills INTEGER NOT NULL DEFAULT 0,
                deaths INTEGER NOT NULL DEFAULT 0,
                kdr REAL NOT NULL DEFAULT 0.0,
                headshot_pct REAL NOT NULL DEFAULT 0.0,
                accuracy_pct REAL NOT NULL DEFAULT 0.0,
                reaction_time_ms REAL NOT NULL DEFAULT 250.0,
                movement_speed REAL NOT NULL DEFAULT 5.0,
                actions_per_second REAL NOT NULL DEFAULT 5.0,
                session_duration_s REAL NOT NULL DEFAULT 300.0,
                is_simulated INTEGER NOT NULL DEFAULT 0,
                cheat_profile VARCHAR(50) DEFAULT 'None',
                recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (room_id) REFERENCES game_rooms(room_id) ON DELETE CASCADE,
                FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
            );
            CREATE TABLE IF NOT EXISTS detection_results (
                detection_id INTEGER PRIMARY KEY AUTOINCREMENT,
                stat_id INTEGER NOT NULL UNIQUE,
                room_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                prediction VARCHAR(20) NOT NULL,
                cheat_probability REAL NOT NULL,
                risk_level VARCHAR(20) NOT NULL,
                anomaly_flags TEXT,
                model_name VARCHAR(100) DEFAULT 'Random Forest v1.0',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (stat_id) REFERENCES gameplay_stats(stat_id) ON DELETE CASCADE,
                FOREIGN KEY (room_id) REFERENCES game_rooms(room_id) ON DELETE CASCADE,
                FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
            );
            CREATE TABLE IF NOT EXISTS moderator_reviews (
                review_id INTEGER PRIMARY KEY AUTOINCREMENT,
                detection_id INTEGER NOT NULL UNIQUE,
                moderator_id INTEGER NOT NULL,
                decision VARCHAR(50) NOT NULL DEFAULT 'Needs Further Review',
                notes TEXT,
                action_taken VARCHAR(50) DEFAULT 'Under Observation',
                reviewed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (detection_id) REFERENCES detection_results(detection_id) ON DELETE CASCADE,
                FOREIGN KEY (moderator_id) REFERENCES users(user_id) ON DELETE CASCADE
            );
        """)

    conn.commit()

    # Seed Default Accounts (password: password123)
    default_pw_hash = generate_password_hash('password123')
    demo_users = [
        ('player1', 'player', '#6366f1'),
        ('player2', 'player', '#06b6d4'),
        ('player3', 'player', '#10b981'),
        ('player4', 'player', '#f59e0b'),
        ('player5', 'player', '#ec4899'),
        ('moderator1', 'moderator', '#8b5cf6')
    ]

    for username, role, color in demo_users:
        cur.execute("SELECT user_id FROM users WHERE username = ?", (username,))
        if not cur.fetchone():
            cur.execute("""
                INSERT INTO users (username, password_hash, role, avatar_color)
                VALUES (?, ?, ?, ?)
            """, (username, default_pw_hash, role, color))

    conn.commit()

    # Seed an Initial Active Room if none exists so users can join immediately
    cur.execute("SELECT COUNT(*) as count FROM game_rooms")
    if cur.fetchone()['count'] == 0:
        cur.execute("SELECT user_id FROM users WHERE username = 'player1'")
        host = cur.fetchone()
        if host:
            host_id = host['user_id']
            room_code = "ARENA-01"
            cur.execute("""
                INSERT INTO game_rooms (room_code, room_name, host_id, status, min_players, max_players)
                VALUES (?, ?, ?, 'waiting', 5, 10)
            """, (room_code, "Championship Tournament Arena", host_id))
            room_id = cur.lastrowid
            
            # Add host as player
            cur.execute("""
                INSERT INTO game_players (room_id, user_id, is_host, is_bot, player_status)
                VALUES (?, ?, 1, 0, 'ready')
            """, (room_id, host_id))
            conn.commit()

    cur.close()
    conn.close()
    print("Database initialized successfully at:", DB_PATH)

def generate_room_code(length=6):
    """Generates an alphanumeric room code (e.g. ROOM-784 or GAMEXY)."""
    chars = string.ascii_uppercase + string.digits
    code = ''.join(random.choices(chars, k=length))
    return f"ROOM-{code[:4]}"

if __name__ == '__main__':
    init_db()
