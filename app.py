"""
FORGE — Personal Training Tracker
Python Flask Backend
"""

import os
from datetime import datetime
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from supabase import create_client, Client

# ── Load environment variables ──
load_dotenv()

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

# ── Initialize Flask ──
app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'forge-dev-key')

# ── Initialize Supabase ──
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


# ═══════════════════════════════════════════════
#   PAGES
# ═══════════════════════════════════════════════

@app.route('/')
def index():
    """Serve the main FORGE app."""
    return render_template('index.html')


# ═══════════════════════════════════════════════
#   BODY LOGS API
# ═══════════════════════════════════════════════

@app.route('/api/body', methods=['GET'])
def get_body_logs():
    """Get all body metric logs, newest first."""
    try:
        response = supabase.table('body_logs') \
            .select('*') \
            .order('date', desc=True) \
            .execute()
        return jsonify({'status': 'ok', 'data': response.data})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/body', methods=['POST'])
def add_body_log():
    """Add a new body metric entry."""
    try:
        data = request.get_json()
        entry = {
            'date': data.get('date', datetime.now().strftime('%Y-%m-%d')),
            'weight': data.get('weight'),
            'waist': data.get('waist'),
            'notes': data.get('notes', '')
        }
        response = supabase.table('body_logs').insert(entry).execute()
        return jsonify({'status': 'ok', 'data': response.data})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/body/<int:log_id>', methods=['DELETE'])
def delete_body_log(log_id):
    """Delete a body metric entry by ID."""
    try:
        supabase.table('body_logs').delete().eq('id', log_id).execute()
        return jsonify({'status': 'ok'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/body/clear', methods=['DELETE'])
def clear_body_logs():
    """Clear all body metric logs."""
    try:
        supabase.table('body_logs').delete().neq('id', 0).execute()
        return jsonify({'status': 'ok'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


# ═══════════════════════════════════════════════
#   WORKOUT LOGS API
# ═══════════════════════════════════════════════

@app.route('/api/workout', methods=['GET'])
def get_workout_logs():
    """Get all workout logs, newest first."""
    try:
        response = supabase.table('workout_logs') \
            .select('*') \
            .order('date', desc=True) \
            .execute()
        return jsonify({'status': 'ok', 'data': response.data})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/workout', methods=['POST'])
def add_workout_log():
    """Add a new workout log entry."""
    try:
        data = request.get_json()
        entry = {
            'date': data.get('date', datetime.now().strftime('%Y-%m-%d')),
            'session': data.get('session', ''),
            'exercise': data.get('exercise'),
            'weight': data.get('weight', 0),
            'sets': data.get('sets', 0),
            'reps': data.get('reps', ''),
        }
        response = supabase.table('workout_logs').insert(entry).execute()
        return jsonify({'status': 'ok', 'data': response.data})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/workout/<int:log_id>', methods=['DELETE'])
def delete_workout_log(log_id):
    """Delete a workout log entry by ID."""
    try:
        supabase.table('workout_logs').delete().eq('id', log_id).execute()
        return jsonify({'status': 'ok'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/workout/clear', methods=['DELETE'])
def clear_workout_logs():
    """Clear all workout logs."""
    try:
        supabase.table('workout_logs').delete().neq('id', 0).execute()
        return jsonify({'status': 'ok'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


# ═══════════════════════════════════════════════
#   STATS API
# ═══════════════════════════════════════════════

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get dashboard stats — latest body metrics + workout summary."""
    try:
        # Latest body log
        body = supabase.table('body_logs') \
            .select('*') \
            .order('date', desc=True) \
            .limit(1) \
            .execute()

        # Workout count
        workouts = supabase.table('workout_logs') \
            .select('id', count='exact') \
            .execute()

        # Unique exercise count
        exercises = supabase.table('workout_logs') \
            .select('exercise') \
            .execute()
        unique_exercises = len(set(e['exercise'] for e in exercises.data)) if exercises.data else 0

        # Personal records (max weight per exercise)
        prs = {}
        if exercises.data:
            all_logs = supabase.table('workout_logs') \
                .select('exercise,weight') \
                .order('weight', desc=True) \
                .execute()
            for log in all_logs.data:
                ex = log['exercise']
                if ex not in prs or (log['weight'] or 0) > (prs[ex] or 0):
                    prs[ex] = log['weight']

        stats = {
            'latest_body': body.data[0] if body.data else None,
            'total_sets': workouts.count if workouts.count else len(workouts.data),
            'unique_exercises': unique_exercises,
            'personal_records': prs
        }
        return jsonify({'status': 'ok', 'data': stats})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


# ═══════════════════════════════════════════════
#   HEALTH CHECK
# ═══════════════════════════════════════════════

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint."""
    try:
        supabase.table('body_logs').select('id').limit(1).execute()
        return jsonify({'status': 'ok', 'database': 'connected'})
    except Exception:
        return jsonify({'status': 'ok', 'database': 'disconnected'})


# ═══════════════════════════════════════════════
#   RUN
# ═══════════════════════════════════════════════

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
