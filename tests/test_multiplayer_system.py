"""
Comprehensive Multiplayer Anti-Cheat System Test Suite
Tests:
- Player & Moderator Authentication
- Multiplayer Room Lobby (5-Player Quorum & Host-Only Start)
- Simulated & Live Interactive Gameplay Submission
- Random Forest ML Evaluation & Anomaly Detection
- Live Dashboard & Chart Aggregations
- Human Moderator Review Audit Workflow
"""

import os
import sys
import unittest
import json

# Ensure project root is in sys.path
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from backend.app import app
from backend.database import get_db, init_db

class TestMultiplayerSystem(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        app.config['TESTING'] = True
        app.config['SECRET_KEY'] = 'test_secret_key_12345'
        cls.client = app.test_client()
        init_db()

    def test_01_user_authentication(self):
        """Test registration, duplicate prevention, and login for player and moderator"""
        # Register new unique player
        reg_resp = self.client.post('/api/auth/register', json={
            'username': 'test_pilot_99',
            'password': 'securepassword123',
            'role': 'player'
        })
        self.assertEqual(reg_resp.status_code, 200)
        data = reg_resp.get_json()
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['user']['username'], 'test_pilot_99')

        # Prevent duplicate username
        dup_resp = self.client.post('/api/auth/register', json={
            'username': 'test_pilot_99',
            'password': 'anotherpassword'
        })
        self.assertEqual(dup_resp.status_code, 409)

        # Login with correct credentials
        login_resp = self.client.post('/api/auth/login', json={
            'username': 'test_pilot_99',
            'password': 'securepassword123'
        })
        self.assertEqual(login_resp.status_code, 200)
        login_data = login_resp.get_json()
        self.assertEqual(login_data['user']['username'], 'test_pilot_99')

        # Check me endpoint
        me_resp = self.client.get('/api/auth/me')
        self.assertEqual(me_resp.status_code, 200)
        self.assertEqual(me_resp.get_json()['status'], 'authenticated')

    def test_02_room_creation_and_joining(self):
        """Test creating room, auto-joining as host, and another user joining"""
        # Login as player1
        self.client.post('/api/auth/login', json={'username': 'player1', 'password': 'password123'})
        
        # Create room
        create_resp = self.client.post('/api/rooms', json={'room_name': 'Test Championship'})
        self.assertEqual(create_resp.status_code, 200)
        room_data = create_resp.get_json()
        room_id = room_data['room_id']
        self.assertIsNotNone(room_id)

        # Fetch room detail (should have 1 player: host)
        detail_resp = self.client.get(f'/api/rooms/{room_id}')
        self.assertEqual(detail_resp.status_code, 200)
        detail = detail_resp.get_json()['room']
        self.assertEqual(detail['player_count'], 1)
        self.assertFalse(detail['can_start']) # False because < 5 players

        # Login as player2 and join room
        self.client.post('/api/auth/login', json={'username': 'player2', 'password': 'password123'})
        join_resp = self.client.post(f'/api/rooms/{room_id}/join')
        self.assertEqual(join_resp.status_code, 200)

        # Verify count is now 2
        detail_resp = self.client.get(f'/api/rooms/{room_id}')
        self.assertEqual(detail_resp.get_json()['room']['player_count'], 2)

    def test_03_minimum_five_player_validation(self):
        """Test that game CANNOT start when fewer than 5 players have joined"""
        # Login as player1 (host of test room)
        self.client.post('/api/auth/login', json={'username': 'player1', 'password': 'password123'})
        create_resp = self.client.post('/api/rooms', json={'room_name': 'Quorum Test Room'})
        room_id = create_resp.get_json()['room_id']

        # Attempt to start with only 1 player -> Must fail with 400
        start_resp = self.client.post(f'/api/rooms/{room_id}/start')
        self.assertEqual(start_resp.status_code, 400)
        data = start_resp.get_json()
        self.assertIn("Minimum 5 players required", data['message'])

        # Non-host cannot start either
        self.client.post('/api/auth/login', json={'username': 'player2', 'password': 'password123'})
        non_host_resp = self.client.post(f'/api/rooms/{room_id}/start')
        self.assertEqual(non_host_resp.status_code, 403)

    def test_04_quick_fill_and_match_start(self):
        """Test quick-fill brings players to 5 and allows host to start game and evaluate ML"""
        # Login as player1
        self.client.post('/api/auth/login', json={'username': 'player1', 'password': 'password123'})
        create_resp = self.client.post('/api/rooms', json={'room_name': 'Full Tournament Room'})
        room_id = create_resp.get_json()['room_id']

        # Quick fill to 5 players
        fill_resp = self.client.post(f'/api/rooms/{room_id}/quick-fill')
        self.assertEqual(fill_resp.status_code, 200)
        self.assertGreaterEqual(fill_resp.get_json()['player_count'], 5)

        # Verify room status can_start is now True
        detail_resp = self.client.get(f'/api/rooms/{room_id}')
        self.assertTrue(detail_resp.get_json()['room']['can_start'])

        # Host starts match
        start_resp = self.client.post(f'/api/rooms/{room_id}/start')
        self.assertEqual(start_resp.status_code, 200)
        result = start_resp.get_json()
        self.assertEqual(result['status'], 'success')
        self.assertGreaterEqual(len(result['results']), 5)

        # Check that predictions have probability and risk_level
        first_res = result['results'][0]
        self.assertIn('prediction', first_res)
        self.assertIn('cheat_probability', first_res)
        self.assertIn('risk_level', first_res)

    def test_05_live_interactive_gameplay_submission(self):
        """Test submitting real interactive telemetry from Target Reflex mini-game (is_simulated = 0)"""
        self.client.post('/api/auth/login', json={'username': 'player1', 'password': 'password123'})
        
        live_stats = {
            'kills': 14,
            'deaths': 3,
            'headshot_pct': 35.0,
            'accuracy_pct': 52.0,
            'reaction_time_ms': 225.0,
            'movement_speed': 5.8,
            'actions_per_second': 6.2,
            'session_duration_s': 60.0
        }
        resp = self.client.post('/api/gameplay/submit-live', json=live_stats)
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['stats']['is_simulated'], 0) # Real interactive telemetry!
        self.assertIn('cheat_probability', data)
        self.assertIn('prediction', data)

    def test_06_live_detection_dashboard_and_charts(self):
        """Test dashboard metrics and chart payloads (bar, pie, scatter, line)"""
        resp = self.client.get('/api/detection/dashboard')
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertEqual(data['status'], 'success')

        # KPI verification
        kpi = data['kpi']
        self.assertIn('total_players', kpi)
        self.assertIn('legitimate_players', kpi)
        self.assertIn('suspicious_players', kpi)
        self.assertIn('avg_cheat_probability', kpi)

        # Chart format verification
        charts = data['charts']
        self.assertIn('bar', charts)
        self.assertIn('pie', charts)
        self.assertIn('scatter', charts)
        self.assertIn('line', charts)

        # Scatter plot check (accuracy vs reaction time)
        self.assertIsInstance(charts['scatter'], list)
        if len(charts['scatter']) > 0:
            first_pt = charts['scatter'][0]
            self.assertIn('x', first_pt) # accuracy_pct
            self.assertIn('y', first_pt) # reaction_time_ms
            self.assertIn('prediction', first_pt)

    def test_07_moderator_review_workflow(self):
        """Test moderator queue retrieval and audit decision recording (human-in-the-loop)"""
        # Login as moderator1
        self.client.post('/api/auth/login', json={'username': 'moderator1', 'password': 'password123'})
        
        # Get queue
        queue_resp = self.client.get('/api/moderator/queue')
        self.assertEqual(queue_resp.status_code, 200)
        queue_data = queue_resp.get_json()
        self.assertIn('queue', queue_data)
        self.assertGreater(len(queue_data['queue']), 0)

        # Take first detection item to review
        item = queue_data['queue'][0]
        det_id = item['detection_id']

        # Submit human audit decision
        review_resp = self.client.post('/api/moderator/review', json={
            'detection_id': det_id,
            'decision': 'Confirmed Cheating',
            'notes': 'Audited reaction time <110ms and abnormal headshot clustering.',
            'action_taken': 'Warning Issued'
        })
        self.assertEqual(review_resp.status_code, 200)

        # Verify review is reflected in queue
        queue_resp2 = self.client.get('/api/moderator/queue')
        updated_item = next((q for q in queue_resp2.get_json()['queue'] if q['detection_id'] == det_id), None)
        self.assertIsNotNone(updated_item)
        self.assertEqual(updated_item['decision'], 'Confirmed Cheating')

    def test_08_model_metadata(self):
        """Test retrieving Random Forest model metadata and feature importances"""
        resp = self.client.get('/api/model/info')
        self.assertEqual(resp.status_code, 200)
        meta = resp.get_json()['metadata']
        self.assertEqual(meta['model_name'], 'Random Forest Classifier')
        self.assertIn('accuracy', meta)
        self.assertIn('feature_importances', meta)

if __name__ == '__main__':
    print("=" * 80)
    print(" RUNNING MULTIPLAYER IN-GAME CHEAT DETECTION SYSTEM TEST SUITE")
    print("=" * 80)
    unittest.main()
