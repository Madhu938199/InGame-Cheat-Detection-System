"""
Flask Application & Multiplayer Anti-Cheat Backend Server
Project: Multiplayer In-Game Cheat Detection System
File: backend/app.py
"""

import os
import sys
from functools import wraps
from flask import Flask, render_template, request, jsonify, session, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash

# Ensure project root is in sys.path
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from backend.database import (
    get_db, init_db, generate_room_code,
    get_room_players, set_player_readiness,
    set_player_online_status, update_player_score,
    validate_room_start_conditions
)
from backend.prediction import predict_player_cheat, get_model_metadata
from backend.game_sim import (
    simulate_and_evaluate_match,
    quick_fill_room_with_demo_players,
    generate_player_gameplay_stats
)

template_dir = os.path.join(BASE_DIR, 'templates')
static_dir = os.path.join(BASE_DIR, 'static')

app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
app.secret_key = os.environ.get('SECRET_KEY', 'multiplayer_cheat_detection_secret_2026')

# Initialize Flask-SocketIO with graceful fallback
try:
    from flask_socketio import SocketIO, emit, join_room, leave_room
    SOCKETIO_AVAILABLE = True
    socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading', manage_session=False)
except ImportError:
    SOCKETIO_AVAILABLE = False
    socketio = None
    emit = None
    join_room = None
    leave_room = None

# Initialize DB on server start
with app.app_context():
    try:
        init_db()
    except Exception as e:
        print(f"Database init warning: {e}")

# -------------------------------------------------------------
# AUTHENTICATION HELPERS & DECORATORS
# -------------------------------------------------------------
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({"status": "error", "message": "Authentication required. Please sign in."}), 401
        return f(*args, **kwargs)
    return decorated_function

def moderator_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({"status": "error", "message": "Authentication required."}), 401
        if session.get('role') != 'moderator':
            return jsonify({"status": "error", "message": "Moderator privilege required."}), 403
        return f(*args, **kwargs)
    return decorated_function

# -------------------------------------------------------------
# FRONTEND SPA SERVING
# -------------------------------------------------------------
@app.route('/')
def index():
    return render_template('index.html')

# -------------------------------------------------------------
# 1. PLAYER AUTHENTICATION ENDPOINTS
# -------------------------------------------------------------
@app.route('/api/auth/register', methods=['POST'])
def api_register():
    data = request.get_json() or {}
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()
    role = data.get('role', 'player').strip().lower()

    if not username or not password:
        return jsonify({"status": "error", "message": "Username and password are required"}), 400

    if role not in ['player', 'moderator']:
        role = 'player'

    conn = get_db()
    cur = conn.cursor()
    try:
        cur.execute("SELECT user_id FROM users WHERE username = ?", (username,))
        if cur.fetchone():
            return jsonify({"status": "error", "message": f"Username '{username}' is already taken"}), 409

        password_hash = generate_password_hash(password)
        colors = ['#6366f1', '#8b5cf6', '#ec4899', '#06b6d4', '#10b981', '#f59e0b']
        import random
        avatar_color = random.choice(colors)

        cur.execute("""
            INSERT INTO users (username, password_hash, role, avatar_color)
            VALUES (?, ?, ?, ?)
        """, (username, password_hash, role, avatar_color))
        user_id = cur.lastrowid
        conn.commit()

        session['user_id'] = user_id
        session['username'] = username
        session['role'] = role

        return jsonify({
            "status": "success",
            "message": "Registration successful",
            "user": {
                "user_id": user_id,
                "username": username,
                "role": role,
                "avatar_color": avatar_color
            }
        })
    except Exception as e:
        conn.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        cur.close()
        conn.close()

@app.route('/api/auth/login', methods=['POST'])
def api_login():
    data = request.get_json() or {}
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()

    if not username or not password:
        return jsonify({"status": "error", "message": "Username and password are required"}), 400

    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cur.fetchone()
    cur.close()
    conn.close()

    if user and check_password_hash(user['password_hash'], password):
        session['user_id'] = user['user_id']
        session['username'] = user['username']
        session['role'] = user['role']

        return jsonify({
            "status": "success",
            "message": "Login successful",
            "user": {
                "user_id": user['user_id'],
                "username": user['username'],
                "role": user['role'],
                "avatar_color": user['avatar_color'] or '#6366f1'
            }
        })

    return jsonify({"status": "error", "message": "Invalid username or password"}), 401

@app.route('/api/auth/logout', methods=['POST'])
def api_logout():
    session.clear()
    return jsonify({"status": "success", "message": "Logged out successfully"})

@app.route('/api/auth/me', methods=['GET'])
def api_me():
    if 'user_id' not in session:
        return jsonify({"status": "unauthenticated", "user": None})

    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT user_id, username, role, avatar_color FROM users WHERE user_id = ?", (session['user_id'],))
    user = cur.fetchone()
    cur.close()
    conn.close()

    if not user:
        session.clear()
        return jsonify({"status": "unauthenticated", "user": None})

    return jsonify({
        "status": "authenticated",
        "user": dict(user)
    })

# -------------------------------------------------------------
# 2. MULTIPLAYER GAME LOBBY & ROOM MANAGEMENT
# -------------------------------------------------------------
@app.route('/api/rooms', methods=['GET'])
def api_get_rooms():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT r.*, u.username as host_name,
               (SELECT COUNT(*) FROM game_players gp WHERE gp.room_id = r.room_id) as player_count
        FROM game_rooms r
        JOIN users u ON r.host_id = u.user_id
        ORDER BY r.created_at DESC LIMIT 20
    """)
    rooms = [dict(row) for row in cur.fetchall()]
    cur.close()
    conn.close()
    return jsonify({"status": "success", "rooms": rooms})

@app.route('/api/rooms', methods=['POST'])
@login_required
def api_create_room():
    data = request.get_json() or {}
    room_name = data.get('room_name', '').strip() or f"{session['username']}'s Match"
    host_id = session['user_id']
    room_code = generate_room_code()

    conn = get_db()
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO game_rooms (room_code, room_name, host_id, status, min_players, max_players)
            VALUES (?, ?, ?, 'waiting', 5, 10)
        """, (room_code, room_name, host_id))
        room_id = cur.lastrowid

        # Automatically join host to room
        cur.execute("""
            INSERT INTO game_players (room_id, user_id, is_host, is_bot, player_status)
            VALUES (?, ?, 1, 0, 'ready')
        """, (room_id, host_id))
        conn.commit()

        return jsonify({
            "status": "success",
            "message": "Room created successfully",
            "room_id": room_id,
            "room_code": room_code
        })
    except Exception as e:
        conn.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        cur.close()
        conn.close()

@app.route('/api/rooms/<int:room_id>', methods=['GET'])
def api_get_room_detail(room_id):
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        SELECT r.*, u.username as host_name
        FROM game_rooms r
        JOIN users u ON r.host_id = u.user_id
        WHERE r.room_id = ?
    """, (room_id,))
    room = cur.fetchone()

    if not room:
        cur.close()
        conn.close()
        return jsonify({"status": "error", "message": "Room not found"}), 404

    cur.execute("""
        SELECT gp.id as roster_id, gp.user_id, gp.is_host, gp.is_bot, gp.player_status,
               COALESCE(gp.is_online, 1) as is_online, COALESCE(gp.score, 0) as score, gp.joined_at,
               u.username, u.role, u.avatar_color
        FROM game_players gp
        JOIN users u ON gp.user_id = u.user_id
        WHERE gp.room_id = ?
        ORDER BY gp.is_host DESC, gp.joined_at ASC
    """, (room_id,))
    players = [dict(p) for p in cur.fetchall()]
    cur.close()
    conn.close()

    room_dict = dict(room)
    room_dict['players'] = players
    room_dict['player_count'] = len(players)
    ready_count = sum(1 for p in players if p['player_status'] == 'ready')
    room_dict['ready_count'] = ready_count
    
    # Requirement: Can start only when AT LEAST 5 players are connected AND ready
    quorum_met = len(players) >= room_dict['min_players']
    all_ready = (len(players) > 0) and (ready_count == len(players))
    room_dict['can_start'] = quorum_met and all_ready
    room_dict['is_current_user_host'] = (session.get('user_id') == room_dict['host_id'])

    return jsonify({"status": "success", "room": room_dict})

@app.route('/api/rooms/<int:room_id>/join', methods=['POST'])
@login_required
def api_join_room(room_id):
    user_id = session['user_id']
    conn = get_db()
    cur = conn.cursor()

    try:
        cur.execute("SELECT * FROM game_rooms WHERE room_id = ?", (room_id,))
        room = cur.fetchone()
        if not room:
            return jsonify({"status": "error", "message": "Room not found"}), 404

        if room['status'] != 'waiting':
            return jsonify({"status": "error", "message": "Game is already in progress or completed"}), 400

        cur.execute("SELECT COUNT(*) as count FROM game_players WHERE room_id = ?", (room_id,))
        count = cur.fetchone()['count']
        if count >= room['max_players']:
            return jsonify({"status": "error", "message": "Room is full"}), 400

        # Prevent duplicate player entries in the same room
        cur.execute("SELECT id FROM game_players WHERE room_id = ? AND user_id = ?", (room_id, user_id))
        if cur.fetchone():
            return jsonify({"status": "success", "message": "Already in room", "room_id": room_id})

        cur.execute("""
            INSERT INTO game_players (room_id, user_id, is_host, is_bot, player_status, is_online, score)
            VALUES (?, ?, 0, 0, 'ready', 1, 0)
        """, (room_id, user_id))
        conn.commit()

        if socketio:
            socketio.emit('room_update', {
                'room_id': room_id,
                'players': get_room_players(room_id)
            }, room=f"room_{room_id}")

        return jsonify({"status": "success", "message": "Joined room successfully", "room_id": room_id})
    except Exception as e:
        conn.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        cur.close()
        conn.close()

@app.route('/api/rooms/<int:room_id>/leave', methods=['POST'])
@login_required
def api_leave_room(room_id):
    user_id = session['user_id']
    conn = get_db()
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM game_players WHERE room_id = ? AND user_id = ?", (room_id, user_id))
        conn.commit()

        if socketio:
            socketio.emit('room_update', {
                'room_id': room_id,
                'players': get_room_players(room_id)
            }, room=f"room_{room_id}")

        return jsonify({"status": "success", "message": "Left room"})
    finally:
        cur.close()
        conn.close()

@app.route('/api/rooms/<int:room_id>/ready', methods=['POST'])
@login_required
def api_toggle_player_ready(room_id):
    """Toggles readiness status of the logged-in player."""
    user_id = session['user_id']
    data = request.get_json() or {}
    
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT player_status FROM game_players WHERE room_id = ? AND user_id = ?", (room_id, user_id))
    row = cur.fetchone()
    if not row:
        cur.close()
        conn.close()
        return jsonify({"status": "error", "message": "You are not joined to this room."}), 400

    # Toggle or explicitly set
    current_status = row['player_status']
    new_status = 'not_ready' if current_status == 'ready' else 'ready'
    if 'ready' in data:
        new_status = 'ready' if data['ready'] else 'not_ready'

    cur.execute("UPDATE game_players SET player_status = ? WHERE room_id = ? AND user_id = ?", (new_status, room_id, user_id))
    conn.commit()
    cur.close()
    conn.close()

    if socketio:
        socketio.emit('room_update', {
            'room_id': room_id,
            'players': get_room_players(room_id)
        }, room=f"room_{room_id}")

    return jsonify({
        "status": "success",
        "player_status": new_status,
        "is_ready": (new_status == 'ready'),
        "user_id": user_id
    })

@app.route('/api/rooms/<int:room_id>/quick-ready', methods=['POST'])
@login_required
def api_quick_ready_room(room_id):
    """Sets all players in the room to ready for seamless viva demonstration."""
    conn = get_db()
    cur = conn.cursor()
    cur.execute("UPDATE game_players SET player_status = 'ready' WHERE room_id = ?", (room_id,))
    conn.commit()
    cur.close()
    conn.close()

    players = get_room_players(room_id)
    if socketio:
        socketio.emit('room_update', {
            'room_id': room_id,
            'players': players
        }, room=f"room_{room_id}")

    return jsonify({"status": "success", "message": "All room players are now ready!", "players": players})

@app.route('/api/rooms/<int:room_id>/quick-fill', methods=['POST'])
@login_required
def api_quick_fill_room(room_id):
    """
    Demonstration accelerator:
    Adds registered test players (player2, player3, player4, player5)
    to reach the required minimum 5 players in one click.
    """
    new_count = quick_fill_room_with_demo_players(room_id)
    players = get_room_players(room_id)

    if socketio:
        socketio.emit('room_update', {
            'room_id': room_id,
            'players': players
        }, room=f"room_{room_id}")

    return jsonify({
        "status": "success",
        "message": f"Room now has {new_count} players (threshold met: {new_count >= 5})",
        "player_count": new_count
    })

@app.route('/api/rooms/<int:room_id>/score', methods=['POST'])
@login_required
def api_record_player_score(room_id):
    """Updates real-time score for current player and broadcasts to room."""
    data = request.get_json() or {}
    score = int(data.get('score', 0))
    user_id = session['user_id']
    username = session.get('username', 'Player')

    update_player_score(room_id, user_id, score)

    if socketio:
        socketio.emit('score_update', {
            'room_id': room_id,
            'user_id': user_id,
            'username': username,
            'score': score
        }, room=f"room_{room_id}")

    return jsonify({"status": "success", "score": score})

@app.route('/api/rooms/<int:room_id>/scores', methods=['GET'])
def api_get_room_scores(room_id):
    """Returns live scoreboard for all players in room."""
    players = get_room_players(room_id)
    leaderboard = [
        {
            'user_id': p['user_id'],
            'username': p['username'],
            'avatar_color': p.get('avatar_color', '#6366f1'),
            'score': p.get('score', 0),
            'player_status': p.get('player_status', 'ready'),
            'is_online': p.get('is_online', 1)
        }
        for p in players
    ]
    leaderboard.sort(key=lambda x: x['score'], reverse=True)
    return jsonify({"status": "success", "scores": leaderboard})

# -------------------------------------------------------------
# 3. GAME SIMULATION & MATCH EXECUTION (MINIMUM 5 PLAYERS)
# -------------------------------------------------------------
@app.route('/api/rooms/<int:room_id>/start', methods=['POST'])
@login_required
def api_start_room_game(room_id):
    """
    Starts game room and runs ML cheat detection.
    STRICT REQUIREMENTS:
    - Only room host can start the game.
    - Minimum 5 unique registered players required!
    - All players in room must be ready!
    - Emits game_started event to all room players simultaneously.
    """
    user_id = session['user_id']
    can_start, err_msg, room_dict = validate_room_start_conditions(room_id, user_id)
    if not can_start:
        status_code = 403 if "Permission denied" in (err_msg or "") else 400
        return jsonify({"status": "error", "message": err_msg}), status_code

    # Broadcast game-start event to all room participants via WebSocket
    players = get_room_players(room_id)
    if socketio:
        socketio.emit('game_started', {
            'room_id': room_id,
            'room_name': room_dict.get('room_name', 'Championship Match'),
            'duration': 30,
            'players': [{'user_id': p['user_id'], 'username': p['username'], 'score': 0} for p in players]
        }, room=f"room_{room_id}")

    # Execute telemetry collection and ML inference for all 5+ room players
    success, result_or_err = simulate_and_evaluate_match(room_id)
    if not success:
        return jsonify({"status": "error", "message": result_or_err}), 400

    return jsonify({
        "status": "success",
        "message": "Game started & telemetry analyzed by Random Forest model!",
        "results": result_or_err
    })

# -------------------------------------------------------------
# 4. INTERACTIVE SHOOTING RANGE (LIVE GAMEPLAY SUBMISSION)
# -------------------------------------------------------------
@app.route('/api/gameplay/submit-live', methods=['POST'])
@login_required
def api_submit_live_gameplay():
    """
    Submits stats from the interactive in-browser Target Range mini-game.
    Flags is_simulated = 0 (Real human interactive test!).
    """
    data = request.get_json() or {}
    user_id = session['user_id']
    room_id = data.get('room_id', 1)

    kills = int(data.get('kills', 10))
    deaths = int(data.get('deaths', 2))
    kdr = round(kills / max(1, deaths), 2)
    headshot_pct = float(data.get('headshot_pct', 25.0))
    accuracy_pct = float(data.get('accuracy_pct', 45.0))
    reaction_time_ms = float(data.get('reaction_time_ms', 240.0))
    movement_speed = float(data.get('movement_speed', 5.5))
    actions_per_second = float(data.get('actions_per_second', 6.0))
    session_duration_s = float(data.get('session_duration_s', 60.0))

    stats = {
        'kills': kills,
        'deaths': deaths,
        'kdr': kdr,
        'headshot_pct': headshot_pct,
        'accuracy_pct': accuracy_pct,
        'reaction_time_ms': reaction_time_ms,
        'movement_speed': movement_speed,
        'actions_per_second': actions_per_second,
        'session_duration_s': session_duration_s,
        'is_simulated': 0, # Live interactive play
        'cheat_profile': data.get('cheat_profile', 'None')
    }

    # Evaluate ML prediction
    prediction_result = predict_player_cheat(stats)
    flags_str = ", ".join(prediction_result['anomaly_flags']) if prediction_result['anomaly_flags'] else "None"

    conn = get_db()
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO gameplay_stats (
                room_id, user_id, kills, deaths, kdr, headshot_pct, accuracy_pct,
                reaction_time_ms, movement_speed, actions_per_second, session_duration_s,
                is_simulated, cheat_profile
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            room_id, user_id, kills, deaths, kdr, headshot_pct, accuracy_pct,
            reaction_time_ms, movement_speed, actions_per_second, session_duration_s,
            0, stats['cheat_profile']
        ))
        stat_id = cur.lastrowid

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
        conn.commit()

        return jsonify({
            "status": "success",
            "message": "Gameplay telemetry evaluated by Random Forest!",
            "detection_id": detection_id,
            "prediction": prediction_result['prediction'],
            "cheat_probability": prediction_result['cheat_probability'],
            "risk_level": prediction_result['risk_level'],
            "anomaly_flags": prediction_result['anomaly_flags'],
            "stats": stats
        })
    except Exception as e:
        conn.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        cur.close()
        conn.close()

# -------------------------------------------------------------
# 5. LIVE DETECTION DASHBOARD & CHART AGGREGATIONS
# -------------------------------------------------------------
@app.route('/api/detection/dashboard', methods=['GET'])
def api_detection_dashboard():
    """
    Returns complete live detection statistics:
    - Total players evaluated
    - Legitimate count
    - Suspicious count
    - Average cheat probability
    - Player detection rows
    - Chart.js ready datasets (Bar, Pie, Scatter, Line)
    """
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        SELECT dr.*, gs.*, u.username, u.avatar_color,
               COALESCE(mr.decision, 'Under Review') as moderator_decision,
               mr.review_id, mr.notes as moderator_notes
        FROM detection_results dr
        JOIN gameplay_stats gs ON dr.stat_id = gs.stat_id
        JOIN users u ON dr.user_id = u.user_id
        LEFT JOIN moderator_reviews mr ON dr.detection_id = mr.detection_id
        ORDER BY dr.created_at DESC LIMIT 50
    """)
    records = [dict(r) for r in cur.fetchall()]

    total_scans = len(records)
    legit_count = sum(1 for r in records if r['prediction'] == 'Legitimate')
    suspicious_count = sum(1 for r in records if r['prediction'] == 'Suspicious')
    cheating_count = sum(1 for r in records if r['prediction'] == 'Cheating')
    avg_prob = round(sum(r['cheat_probability'] for r in records) / max(1, total_scans), 1)

    # 1. Bar Chart: Player vs Cheat Probability
    top_players = records[:12]
    bar_chart = {
        "labels": [r['username'] for r in top_players],
        "probabilities": [r['cheat_probability'] for r in top_players],
        "colors": [
            '#ef4444' if r['prediction'] == 'Cheating' else
            '#f59e0b' if r['prediction'] == 'Suspicious' else
            '#10b981' for r in top_players
        ],
        "predictions": [r['prediction'] for r in top_players]
    }

    # 2. Pie Chart: Legitimate vs Suspicious vs Cheating (Flowchart Stage H)
    pie_chart = {
        "labels": ["Legitimate Players", "Suspicious / Anomalous", "Cheating / High Risk"],
        "data": [legit_count, suspicious_count, cheating_count],
        "colors": ["#10b981", "#f59e0b", "#ef4444"]
    }

    # 3. Scatter Plot: Accuracy (%) vs Reaction Time (ms)
    # (Shows clear clustering between human biological limits, anomalies, and superhuman bot snaps)
    scatter_data = []
    for r in records:
        scatter_data.append({
            "x": r['accuracy_pct'],
            "y": r['reaction_time_ms'],
            "username": r['username'],
            "prediction": r['prediction'],
            "cheat_probability": r['cheat_probability']
        })

    # 4. Line Chart: Telemetry Trends over Recent Matches
    chronological = list(reversed(records[:15]))
    line_chart = {
        "labels": [f"M-{i+1}" for i in range(len(chronological))],
        "accuracy": [r['accuracy_pct'] for r in chronological],
        "headshot": [r['headshot_pct'] for r in chronological],
        "reaction": [r['reaction_time_ms'] for r in chronological]
    }

    cur.close()
    conn.close()

    return jsonify({
        "status": "success",
        "kpi": {
            "total_players": total_scans,
            "legitimate_players": legit_count,
            "suspicious_players": suspicious_count,
            "cheating_players": cheating_count,
            "avg_cheat_probability": avg_prob
        },
        "records": records,
        "charts": {
            "bar": bar_chart,
            "pie": pie_chart,
            "scatter": scatter_data,
            "line": line_chart
        }
    })

# -------------------------------------------------------------
# 6. MODERATOR DASHBOARD & AUDIT CENTER
# -------------------------------------------------------------
@app.route('/api/moderator/queue', methods=['GET'])
def api_moderator_queue():
    """Returns suspicious players needing human audit review."""
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT dr.*, gs.*, u.username, u.avatar_color,
               COALESCE(mr.decision, 'Under Review') as decision,
               mr.notes, mr.action_taken, mr.reviewed_at,
               mu.username as reviewer_username
        FROM detection_results dr
        JOIN gameplay_stats gs ON dr.stat_id = gs.stat_id
        JOIN users u ON dr.user_id = u.user_id
        LEFT JOIN moderator_reviews mr ON dr.detection_id = mr.detection_id
        LEFT JOIN users mu ON mr.moderator_id = mu.user_id
        ORDER BY dr.cheat_probability DESC, dr.created_at DESC
        LIMIT 50
    """)
    queue = [dict(r) for r in cur.fetchall()]

    # Counts
    pending = sum(1 for q in queue if q['decision'] == 'Under Review' and q['prediction'] in ('Suspicious', 'Cheating'))
    confirmed = sum(1 for q in queue if q['decision'] == 'Confirmed Cheating')
    cleared = sum(1 for q in queue if q['decision'] == 'Legitimate')
    cheating_flagged = sum(1 for q in queue if q['prediction'] == 'Cheating')
    suspicious_flagged = sum(1 for q in queue if q['prediction'] == 'Suspicious')

    cur.close()
    conn.close()

    return jsonify({
        "status": "success",
        "stats": {
            "total_flagged": len(queue),
            "pending_review": pending,
            "confirmed_cheating": confirmed,
            "cleared_legitimate": cleared,
            "cheating_flagged": cheating_flagged,
            "suspicious_flagged": suspicious_flagged
        },
        "queue": queue
    })

@app.route('/api/moderator/review', methods=['POST'])
@login_required
def api_submit_review():
    """
    Submits a human moderator determination:
    - 'Confirmed Cheating'
    - 'Legitimate'
    - 'Needs Further Review'
    Explicitly enforces human-in-the-loop audit (does not blindly auto-ban).
    """
    data = request.get_json() or {}
    detection_id = data.get('detection_id')
    decision = data.get('decision', 'Needs Further Review')
    notes = data.get('notes', '').strip()
    action_taken = data.get('action_taken', 'Under Observation')
    moderator_id = session['user_id']

    if not detection_id:
        return jsonify({"status": "error", "message": "detection_id is required"}), 400

    conn = get_db()
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO moderator_reviews (detection_id, moderator_id, decision, notes, action_taken)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(detection_id) DO UPDATE SET
                decision = excluded.decision,
                notes = excluded.notes,
                action_taken = excluded.action_taken,
                moderator_id = excluded.moderator_id,
                reviewed_at = CURRENT_TIMESTAMP
        """, (detection_id, moderator_id, decision, notes, action_taken))
        conn.commit()

        return jsonify({
            "status": "success",
            "message": f"Review saved: Marked as '{decision}'."
        })
    except Exception as e:
        conn.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        cur.close()
        conn.close()

# -------------------------------------------------------------
# 7. MACHINE LEARNING MODEL METADATA & IMPORTANCE
# -------------------------------------------------------------
@app.route('/api/model/info', methods=['GET'])
def api_model_info():
    meta = get_model_metadata()
    return jsonify({
        "status": "success",
        "metadata": meta
    })

# -------------------------------------------------------------
# 8. DEMO SEED TEST MATCH HELPER
# -------------------------------------------------------------
@app.route('/api/demo/seed-match', methods=['POST'])
def api_seed_demo_match():
    """Seeds an initial 5-player match with realistic telemetry for immediate viva review."""
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT room_id FROM game_rooms ORDER BY room_id LIMIT 1")
    room = cur.fetchone()
    if not room:
        room_code = "ARENA-01"
        cur.execute("SELECT user_id FROM users WHERE username = 'player1'")
        u = cur.fetchone()
        host_id = u['user_id'] if u else 1
        cur.execute("""
            INSERT INTO game_rooms (room_code, room_name, host_id, status, min_players, max_players)
            VALUES (?, 'Championship Arena', ?, 'waiting', 5, 10)
        """, (room_code, host_id))
        room_id = cur.lastrowid
        conn.commit()
    else:
        room_id = room['room_id']
    cur.close()
    conn.close()

    quick_fill_room_with_demo_players(room_id)
    success, result = simulate_and_evaluate_match(room_id)
    return jsonify({"status": "success", "room_id": room_id, "data": result})

if __name__ == '__main__':
    print("Multiplayer In-Game Cheat Detection Server starting on http://127.0.0.1:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
