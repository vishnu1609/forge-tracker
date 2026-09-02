"""
FORGE — Unit Tests for Flask Backend (app.py)

Tests all routes with mocked Supabase.
Run: pytest tests/test_app.py -v
"""

import json
import pytest
from unittest.mock import MagicMock, patch


# ═══════════════════════════════════════════════
#   HOME PAGE
# ═══════════════════════════════════════════════

class TestHomePage:
    """GET / — serves the main FORGE app."""

    def test_home_returns_200(self, client):
        resp = client.get('/')
        assert resp.status_code == 200

    def test_home_returns_html(self, client):
        resp = client.get('/')
        assert b'FORGE' in resp.data

    def test_home_contains_nav(self, client):
        resp = client.get('/')
        assert b'nav-logo' in resp.data
        assert b'nav-burger' in resp.data

    def test_home_contains_sessions(self, client):
        resp = client.get('/')
        for session in [b'Upper', b'Lower', b'Push', b'Pull', b'Legs']:
            assert session in resp.data


# ═══════════════════════════════════════════════
#   BODY LOGS API
# ═══════════════════════════════════════════════

class TestGetBodyLogs:
    """GET /api/body — returns all body metric logs."""

    def test_get_body_logs_success(self, client, mock_supabase):
        mock_supabase.execute.return_value = MagicMock(
            data=[
                {'id': 1, 'date': '2026-09-01', 'weight': 105, 'waist': 35, 'notes': ''},
                {'id': 2, 'date': '2026-08-30', 'weight': 106, 'waist': 35.5, 'notes': ''},
            ]
        )
        resp = client.get('/api/body')
        data = json.loads(resp.data)

        assert resp.status_code == 200
        assert data['status'] == 'ok'
        assert len(data['data']) == 2
        assert data['data'][0]['weight'] == 105

    def test_get_body_logs_empty(self, client, mock_supabase):
        mock_supabase.execute.return_value = MagicMock(data=[])
        resp = client.get('/api/body')
        data = json.loads(resp.data)

        assert resp.status_code == 200
        assert data['data'] == []

    def test_get_body_logs_db_error(self, client, mock_supabase):
        mock_supabase.execute.side_effect = Exception('DB connection failed')
        resp = client.get('/api/body')
        data = json.loads(resp.data)

        assert resp.status_code == 500
        assert data['status'] == 'error'
        assert 'DB connection failed' in data['message']


class TestAddBodyLog:
    """POST /api/body — adds a new body metric entry."""

    def test_add_body_log_success(self, client, mock_supabase):
        mock_supabase.execute.return_value = MagicMock(
            data=[{'id': 3, 'date': '2026-09-02', 'weight': 105, 'waist': 35, 'notes': ''}]
        )
        resp = client.post('/api/body', json={
            'date': '2026-09-02',
            'weight': 105,
            'waist': 35,
        })
        data = json.loads(resp.data)

        assert resp.status_code == 200
        assert data['status'] == 'ok'
        assert data['data'][0]['weight'] == 105

    def test_add_body_log_defaults_date(self, client, mock_supabase):
        mock_supabase.execute.return_value = MagicMock(data=[{'id': 4}])
        resp = client.post('/api/body', json={'weight': 104})

        assert resp.status_code == 200
        # Verify insert was called (date should default to today)
        mock_supabase.insert.assert_called()

    def test_add_body_log_db_error(self, client, mock_supabase):
        mock_supabase.execute.side_effect = Exception('Insert failed')
        resp = client.post('/api/body', json={'weight': 105})
        data = json.loads(resp.data)

        assert resp.status_code == 500
        assert data['status'] == 'error'


class TestDeleteBodyLog:
    """DELETE /api/body/<id> — deletes a body metric entry."""

    def test_delete_body_log_success(self, client, mock_supabase):
        mock_supabase.execute.return_value = MagicMock(data=[])
        resp = client.delete('/api/body/1')
        data = json.loads(resp.data)

        assert resp.status_code == 200
        assert data['status'] == 'ok'

    def test_delete_body_log_db_error(self, client, mock_supabase):
        mock_supabase.execute.side_effect = Exception('Delete failed')
        resp = client.delete('/api/body/1')

        assert resp.status_code == 500


class TestClearBodyLogs:
    """DELETE /api/body/clear — clears all body metric logs."""

    def test_clear_body_logs_success(self, client, mock_supabase):
        mock_supabase.execute.return_value = MagicMock(data=[])
        resp = client.delete('/api/body/clear')
        data = json.loads(resp.data)

        assert resp.status_code == 200
        assert data['status'] == 'ok'

    def test_clear_body_logs_db_error(self, client, mock_supabase):
        mock_supabase.execute.side_effect = Exception('Clear failed')
        resp = client.delete('/api/body/clear')

        assert resp.status_code == 500


# ═══════════════════════════════════════════════
#   WORKOUT LOGS API
# ═══════════════════════════════════════════════

class TestGetWorkoutLogs:
    """GET /api/workout — returns all workout logs."""

    def test_get_workout_logs_success(self, client, mock_supabase):
        mock_supabase.execute.return_value = MagicMock(
            data=[
                {'id': 1, 'date': '2026-09-01', 'session': 'Upper',
                 'exercise': 'Barbell Overhead Press', 'weight': 40, 'sets': 4, 'reps': '5,5,4,4'},
            ]
        )
        resp = client.get('/api/workout')
        data = json.loads(resp.data)

        assert resp.status_code == 200
        assert data['status'] == 'ok'
        assert data['data'][0]['exercise'] == 'Barbell Overhead Press'

    def test_get_workout_logs_empty(self, client, mock_supabase):
        mock_supabase.execute.return_value = MagicMock(data=[])
        resp = client.get('/api/workout')
        data = json.loads(resp.data)

        assert data['data'] == []


class TestAddWorkoutLog:
    """POST /api/workout — adds a new workout log entry."""

    def test_add_workout_log_full(self, client, mock_supabase):
        mock_supabase.execute.return_value = MagicMock(
            data=[{'id': 5, 'exercise': 'Bench Press', 'weight': 60, 'sets': 4, 'reps': '6,6,5,5'}]
        )
        resp = client.post('/api/workout', json={
            'date': '2026-09-02',
            'session': 'Push',
            'exercise': 'Bench Press',
            'weight': 60,
            'sets': 4,
            'reps': '6,6,5,5',
        })
        data = json.loads(resp.data)

        assert resp.status_code == 200
        assert data['status'] == 'ok'

    def test_add_workout_log_minimal(self, client, mock_supabase):
        """Only exercise name provided — rest should default."""
        mock_supabase.execute.return_value = MagicMock(data=[{'id': 6}])
        resp = client.post('/api/workout', json={'exercise': 'Burpees'})

        assert resp.status_code == 200
        call_args = mock_supabase.insert.call_args[0][0]
        assert call_args['exercise'] == 'Burpees'
        assert call_args['weight'] == 0
        assert call_args['sets'] == 0

    def test_add_workout_log_db_error(self, client, mock_supabase):
        mock_supabase.execute.side_effect = Exception('Insert failed')
        resp = client.post('/api/workout', json={'exercise': 'Deadlift'})

        assert resp.status_code == 500


class TestDeleteWorkoutLog:
    """DELETE /api/workout/<id> — deletes a workout log entry."""

    def test_delete_workout_log_success(self, client, mock_supabase):
        mock_supabase.execute.return_value = MagicMock(data=[])
        resp = client.delete('/api/workout/1')

        assert resp.status_code == 200

    def test_delete_workout_log_db_error(self, client, mock_supabase):
        mock_supabase.execute.side_effect = Exception('Delete failed')
        resp = client.delete('/api/workout/999')

        assert resp.status_code == 500


class TestClearWorkoutLogs:
    """DELETE /api/workout/clear — clears all workout logs."""

    def test_clear_workout_logs_success(self, client, mock_supabase):
        mock_supabase.execute.return_value = MagicMock(data=[])
        resp = client.delete('/api/workout/clear')

        assert resp.status_code == 200
        assert json.loads(resp.data)['status'] == 'ok'

    def test_clear_workout_logs_db_error(self, client, mock_supabase):
        mock_supabase.execute.side_effect = Exception('Clear failed')
        resp = client.delete('/api/workout/clear')

        assert resp.status_code == 500


# ═══════════════════════════════════════════════
#   STATS API
# ═══════════════════════════════════════════════

class TestGetStats:
    """GET /api/stats — returns dashboard stats."""

    def test_stats_with_data(self, client, mock_supabase):
        # Mock needs to handle multiple .execute() calls in sequence
        body_result = MagicMock(data=[{'id': 1, 'weight': 105, 'waist': 35}])
        workout_count = MagicMock(data=[{'id': 1}, {'id': 2}], count=2)
        exercises_result = MagicMock(data=[
            {'exercise': 'Bench Press'},
            {'exercise': 'Deadlift'},
            {'exercise': 'Bench Press'},
        ])
        all_logs_result = MagicMock(data=[
            {'exercise': 'Bench Press', 'weight': 80},
            {'exercise': 'Bench Press', 'weight': 60},
            {'exercise': 'Deadlift', 'weight': 100},
        ])

        mock_supabase.execute.side_effect = [
            body_result,
            workout_count,
            exercises_result,
            all_logs_result,
        ]

        resp = client.get('/api/stats')
        data = json.loads(resp.data)

        assert resp.status_code == 200
        assert data['status'] == 'ok'
        assert data['data']['latest_body']['weight'] == 105
        assert data['data']['total_sets'] == 2
        assert data['data']['unique_exercises'] == 2
        assert data['data']['personal_records']['Bench Press'] == 80
        assert data['data']['personal_records']['Deadlift'] == 100

    def test_stats_empty_db(self, client, mock_supabase):
        empty = MagicMock(data=[], count=0)
        mock_supabase.execute.side_effect = [empty, empty, empty]

        resp = client.get('/api/stats')
        data = json.loads(resp.data)

        assert resp.status_code == 200
        assert data['data']['latest_body'] is None
        assert data['data']['unique_exercises'] == 0

    def test_stats_db_error(self, client, mock_supabase):
        mock_supabase.execute.side_effect = Exception('Stats query failed')
        resp = client.get('/api/stats')

        assert resp.status_code == 500


# ═══════════════════════════════════════════════
#   HEALTH CHECK
# ═══════════════════════════════════════════════

class TestHealthCheck:
    """GET /api/health — health check endpoint."""

    def test_health_db_connected(self, client, mock_supabase):
        mock_supabase.execute.return_value = MagicMock(data=[{'id': 1}])
        resp = client.get('/api/health')
        data = json.loads(resp.data)

        assert resp.status_code == 200
        assert data['status'] == 'ok'
        assert data['database'] == 'connected'

    def test_health_db_disconnected(self, client, mock_supabase):
        mock_supabase.execute.side_effect = Exception('Connection refused')
        resp = client.get('/api/health')
        data = json.loads(resp.data)

        assert resp.status_code == 200
        assert data['status'] == 'ok'
        assert data['database'] == 'disconnected'


# ═══════════════════════════════════════════════
#   EDGE CASES
# ═══════════════════════════════════════════════

class TestEdgeCases:
    """Edge cases and invalid inputs."""

    def test_404_on_unknown_route(self, client):
        resp = client.get('/api/nonexistent')
        assert resp.status_code == 404

    def test_method_not_allowed_body(self, client):
        resp = client.put('/api/body')
        assert resp.status_code == 405

    def test_method_not_allowed_workout(self, client):
        resp = client.patch('/api/workout')
        assert resp.status_code == 405

    def test_post_body_empty_json(self, client, mock_supabase):
        mock_supabase.execute.return_value = MagicMock(data=[{'id': 7}])
        resp = client.post('/api/body', json={})

        assert resp.status_code == 200
        call_args = mock_supabase.insert.call_args[0][0]
        assert call_args['weight'] is None
        assert call_args['waist'] is None
        assert call_args['notes'] == ''

    def test_post_workout_empty_json(self, client, mock_supabase):
        mock_supabase.execute.return_value = MagicMock(data=[{'id': 8}])
        resp = client.post('/api/workout', json={})

        assert resp.status_code == 200
        call_args = mock_supabase.insert.call_args[0][0]
        assert call_args['exercise'] is None
        assert call_args['weight'] == 0
        assert call_args['sets'] == 0
