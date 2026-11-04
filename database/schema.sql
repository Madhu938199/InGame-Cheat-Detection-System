-- ==========================================================
-- Multiplayer In-Game Cheat Detection System
-- Database Schema: SQLite / MySQL Compatible
-- Tables:
--   1. users
--   2. game_rooms
--   3. game_players
--   4. gameplay_stats
--   5. detection_results
--   6. moderator_reviews
-- ==========================================================

-- 1. Users Table
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(50) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'player', -- 'player' or 'moderator'
    avatar_color VARCHAR(20) DEFAULT '#6366f1',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Game Rooms Table
CREATE TABLE IF NOT EXISTS game_rooms (
    room_id INTEGER PRIMARY KEY AUTOINCREMENT,
    room_code VARCHAR(10) NOT NULL UNIQUE,
    room_name VARCHAR(100) NOT NULL,
    host_id INTEGER NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'waiting', -- 'waiting', 'in_progress', 'completed'
    min_players INTEGER NOT NULL DEFAULT 5,
    max_players INTEGER NOT NULL DEFAULT 10,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    started_at TIMESTAMP NULL,
    ended_at TIMESTAMP NULL,
    FOREIGN KEY (host_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- 3. Game Players (Lobby / Roster)
CREATE TABLE IF NOT EXISTS game_players (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    room_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    is_host INTEGER NOT NULL DEFAULT 0, -- 1 if host, 0 otherwise
    is_bot INTEGER NOT NULL DEFAULT 0,  -- 1 if simulated player, 0 if real user
    player_status VARCHAR(20) NOT NULL DEFAULT 'ready', -- 'ready', 'not_ready', 'playing', 'finished'
    is_online INTEGER NOT NULL DEFAULT 1, -- 1 if connected, 0 if offline
    score INTEGER NOT NULL DEFAULT 0,    -- Real-time match score
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(room_id, user_id),
    FOREIGN KEY (room_id) REFERENCES game_rooms(room_id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- 4. Gameplay Statistics Table
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
    is_simulated INTEGER NOT NULL DEFAULT 0, -- Clearly distinguishes simulated from real
    cheat_profile VARCHAR(50) DEFAULT 'None', -- For demo ground truth testing
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (room_id) REFERENCES game_rooms(room_id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- 5. Cheat Detection Results Table (ML Random Forest Output)
CREATE TABLE IF NOT EXISTS detection_results (
    detection_id INTEGER PRIMARY KEY AUTOINCREMENT,
    stat_id INTEGER NOT NULL UNIQUE,
    room_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    prediction VARCHAR(20) NOT NULL, -- 'Legitimate' or 'Suspicious'
    cheat_probability REAL NOT NULL, -- 0.0 to 100.0 %
    risk_level VARCHAR(20) NOT NULL, -- 'LOW', 'MEDIUM', 'HIGH'
    anomaly_flags TEXT,              -- Comma-separated or JSON list of detected anomalies
    model_name VARCHAR(100) DEFAULT 'Random Forest v1.0',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (stat_id) REFERENCES gameplay_stats(stat_id) ON DELETE CASCADE,
    FOREIGN KEY (room_id) REFERENCES game_rooms(room_id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- 6. Moderator Reviews Table (Human-in-the-Loop Decision Center)
CREATE TABLE IF NOT EXISTS moderator_reviews (
    review_id INTEGER PRIMARY KEY AUTOINCREMENT,
    detection_id INTEGER NOT NULL UNIQUE,
    moderator_id INTEGER NOT NULL,
    decision VARCHAR(50) NOT NULL DEFAULT 'Needs Further Review', -- 'Confirmed Cheating', 'Legitimate', 'Needs Further Review'
    notes TEXT,
    action_taken VARCHAR(50) DEFAULT 'Under Observation', -- 'Under Observation', 'Warning Issued', 'Account Suspended', 'Cleared'
    reviewed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (detection_id) REFERENCES detection_results(detection_id) ON DELETE CASCADE,
    FOREIGN KEY (moderator_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- Indexing for high-performance dashboard queries
CREATE INDEX IF NOT EXISTS idx_room_code ON game_rooms(room_code);
CREATE INDEX IF NOT EXISTS idx_room_players ON game_players(room_id);
CREATE INDEX IF NOT EXISTS idx_stats_room ON gameplay_stats(room_id);
CREATE INDEX IF NOT EXISTS idx_detection_room ON detection_results(room_id);
CREATE INDEX IF NOT EXISTS idx_detection_prediction ON detection_results(prediction);
