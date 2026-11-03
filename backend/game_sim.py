"""
Game Simulation & Match Engine Service
Project: Multiplayer In-Game Cheat Detection System
File: backend/game_sim.py
"""

import random
import numpy as np
from backend.database import get_db
from backend.prediction import predict_player_cheat

def generate_player_gameplay_stats(cheat_profile='None', is_simulated=1):
    """
    Generates realistic gameplay statistics based on player profile.
    Profiles:
      - 'Legit_Casual': typical casual gamer
      - 'Legit_Average': standard competitive player
      - 'Legit_Pro': high-skill human gamer (respecting biological limits)
      - 'Aimbot': abnormal headshots (>75%) & laser accuracy
      - 'Triggerbot': superhuman reaction time (<90ms)
      - 'Speedhack': impossible movement speed (>12 m/s)
      - 'Spinbot_Macro': extreme actions per second (>25 APS)
    """
    duration = round(random.uniform(180.0, 600.0), 1)

    if cheat_profile == 'Legit_Casual':
        kills = random.randint(2, 6)
        deaths = random.randint(6, 12)
        headshot_pct = round(random.uniform(10.0, 22.0), 1)
        accuracy_pct = round(random.uniform(18.0, 28.0), 1)
        reaction_time = round(random.uniform(260.0, 360.0), 1)
        speed = round(random.uniform(4.5, 5.5), 1)
        aps = round(random.uniform(2.5, 4.5), 1)
    elif cheat_profile == 'Legit_Average':
        kills = random.randint(7, 13)
        deaths = random.randint(5, 9)
        headshot_pct = round(random.uniform(20.0, 35.0), 1)
        accuracy_pct = round(random.uniform(28.0, 42.0), 1)
        reaction_time = round(random.uniform(210.0, 270.0), 1)
        speed = round(random.uniform(5.0, 6.2), 1)
        aps = round(random.uniform(4.5, 7.0), 1)
    elif cheat_profile == 'Legit_Pro':
        kills = random.randint(14, 22)
        deaths = random.randint(3, 7)
        headshot_pct = round(random.uniform(32.0, 48.0), 1)
        accuracy_pct = round(random.uniform(40.0, 56.0), 1)
        reaction_time = round(random.uniform(170.0, 210.0), 1) # Pro human reflex limit
        speed = round(random.uniform(5.8, 6.8), 1)
        aps = round(random.uniform(7.0, 10.5), 1)
    elif cheat_profile == 'Aimbot':
        kills = random.randint(24, 38)
        deaths = random.randint(0, 3)
        headshot_pct = round(random.uniform(78.0, 96.0), 1)
        accuracy_pct = round(random.uniform(82.0, 98.0), 1)
        reaction_time = round(random.uniform(120.0, 160.0), 1)
        speed = round(random.uniform(5.5, 6.8), 1)
        aps = round(random.uniform(6.0, 9.5), 1)
    elif cheat_profile == 'Triggerbot':
        kills = random.randint(20, 32)
        deaths = random.randint(1, 4)
        headshot_pct = round(random.uniform(45.0, 68.0), 1)
        accuracy_pct = round(random.uniform(70.0, 89.0), 1)
        reaction_time = round(random.uniform(35.0, 85.0), 1) # Non-human reflex!
        speed = round(random.uniform(5.2, 6.5), 1)
        aps = round(random.uniform(5.5, 8.5), 1)
    elif cheat_profile == 'Speedhack':
        kills = random.randint(16, 26)
        deaths = random.randint(2, 5)
        headshot_pct = round(random.uniform(25.0, 50.0), 1)
        accuracy_pct = round(random.uniform(45.0, 68.0), 1)
        reaction_time = round(random.uniform(180.0, 250.0), 1)
        speed = round(random.uniform(13.5, 22.0), 1) # Speedhack!
        aps = round(random.uniform(8.0, 15.0), 1)
    else: # Spinbot / Macro
        kills = random.randint(22, 34)
        deaths = random.randint(0, 2)
        headshot_pct = round(random.uniform(65.0, 90.0), 1)
        accuracy_pct = round(random.uniform(65.0, 85.0), 1)
        reaction_time = round(random.uniform(70.0, 130.0), 1)
        speed = round(random.uniform(6.5, 8.5), 1)
        aps = round(random.uniform(24.0, 45.0), 1) # Extreme APM

    kdr = round(kills / max(1, deaths), 2)

    return {
        'kills': kills,
        'deaths': deaths,
        'kdr': kdr,
        'headshot_pct': headshot_pct,
        'accuracy_pct': accuracy_pct,
        'reaction_time_ms': reaction_time,
        'movement_speed': speed,
        'actions_per_second': aps,
        'session_duration_s': duration,
        'is_simulated': is_simulated,
        'cheat_profile': cheat_profile
    }

def quick_fill_room_with_demo_players(room_id):
    """
    Convenience helper for presentations: adds demo players (player2, player3, player4, player5)
    to reach the required 5-player threshold immediately.
    """
    conn = get_db()
    cur = conn.cursor()

    # Get players already in room
    cur.execute("SELECT user_id FROM game_players WHERE room_id = ?", (room_id,))
    existing_user_ids = {row['user_id'] for row in cur.fetchall()}

    # Find users available to join
    cur.execute("SELECT user_id, username FROM users WHERE role = 'player' ORDER BY user_id")
    available_users = cur.fetchall()

    added = 0
    for u in available_users:
        if len(existing_user_ids) >= 5:
            break
        if u['user_id'] not in existing_user_ids:
            cur.execute("""
                INSERT INTO game_players (room_id, user_id, is_host, is_bot, player_status)
                VALUES (?, ?, 0, 0, 'ready')
            """, (room_id, u['user_id']))
            existing_user_ids.add(u['user_id'])
            added += 1

    # If still fewer than 5 users exist in users table, create dynamic demo bots
    bot_counter = 1
    while len(existing_user_ids) < 5:
        bot_name = f"DemoBot_{bot_counter}"
        cur.execute("SELECT user_id FROM users WHERE username = ?", (bot_name,))
        bot = cur.fetchone()
        if not bot:
            from werkzeug.security import generate_password_hash
            cur.execute("""
                INSERT INTO users (username, password_hash, role, avatar_color)
                VALUES (?, ?, 'player', '#9333ea')
            """, (bot_name, generate_password_hash('password123')))
            bot_user_id = cur.lastrowid
        else:
            bot_user_id = bot['user_id']

        if bot_user_id not in existing_user_ids:
            cur.execute("""
                INSERT INTO game_players (room_id, user_id, is_host, is_bot, player_status)
                VALUES (?, ?, 0, 1, 'ready')
            """, (room_id, bot_user_id))
            existing_user_ids.add(bot_user_id)
            added += 1
        bot_counter += 1

    conn.commit()
    cur.close()
    conn.close()
    return len(existing_user_ids)

def simulate_and_evaluate_match(room_id):
    """
    Simulates a complete competitive round for all joined room players (minimum 5 required).
    Evaluates each player's telemetry using the trained Random Forest model.
    Stores stats and detection results into SQLite.
    """
    conn = get_db()
    cur = conn.cursor()

    # Verify at least 5 players in room
    cur.execute("""
        SELECT gp.user_id, u.username, gp.is_host, gp.is_bot
        FROM game_players gp
        JOIN users u ON gp.user_id = u.user_id
        WHERE gp.room_id = ?
    """, (room_id,))
    players = cur.fetchall()

    if len(players) < 5:
        conn.close()
        return False, f"Room has only {len(players)}/5 players. Minimum 5 players required to start game."

    # Mark room as completed / in_progress
    cur.execute("UPDATE game_rooms SET status = 'completed', ended_at = CURRENT_TIMESTAMP WHERE room_id = ?", (room_id,))

    # Profiles to assign: for a realistic presentation, assign:
    # 3-4 legitimate players + 1-2 suspicious cheaters (e.g. Aimbot or Triggerbot)
    profiles_pool = ['Legit_Casual', 'Legit_Average', 'Legit_Pro', 'Aimbot', 'Triggerbot', 'Legit_Average', 'Speedhack']
    random.shuffle(profiles_pool)

    results_summary = []

    for idx, p in enumerate(players):
        user_id = p['user_id']
        username = p['username']

        # Pick profile
        cheat_profile = profiles_pool[idx % len(profiles_pool)]
        stats = generate_player_gameplay_stats(cheat_profile=cheat_profile, is_simulated=1)

        # 1. Store Gameplay Stats
        cur.execute("""
            INSERT INTO gameplay_stats (
                room_id, user_id, kills, deaths, kdr, headshot_pct, accuracy_pct,
                reaction_time_ms, movement_speed, actions_per_second, session_duration_s,
                is_simulated, cheat_profile
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            room_id, user_id, stats['kills'], stats['deaths'], stats['kdr'],
            stats['headshot_pct'], stats['accuracy_pct'], stats['reaction_time_ms'],
            stats['movement_speed'], stats['actions_per_second'], stats['session_duration_s'],
            stats['is_simulated'], stats['cheat_profile']
        ))
        stat_id = cur.lastrowid

        # 2. Run Random Forest ML Inference
        prediction_result = predict_player_cheat(stats)
        flags_str = ", ".join(prediction_result['anomaly_flags']) if prediction_result['anomaly_flags'] else "None"

        # 3. Store Detection Result
        cur.execute("""
            INSERT INTO detection_results (
                stat_id, room_id, user_id, prediction, cheat_probability,
                risk_level, anomaly_flags, model_name
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            stat_id, room_id, user_id,
            prediction_result['prediction'],
            prediction_result['cheat_probability'],
            prediction_result['risk_level'],
            flags_str,
            prediction_result['model_name']
        ))
        detection_id = cur.lastrowid

        results_summary.append({
            'detection_id': detection_id,
            'stat_id': stat_id,
            'user_id': user_id,
            'username': username,
            'prediction': prediction_result['prediction'],
            'cheat_probability': prediction_result['cheat_probability'],
            'risk_level': prediction_result['risk_level'],
            'anomaly_flags': prediction_result['anomaly_flags'],
            'stats': stats
        })

    conn.commit()
    cur.close()
    conn.close()

    return True, results_summary
