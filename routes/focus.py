# ============================================================
# routes/focus.py — Focus Timer Page + Save Session
# Updated: +1 Stack per completed Pomodoro session
# ============================================================

from flask import Blueprint, render_template, request, session, redirect, url_for, jsonify
from db import get_db_connection
from functools import wraps
from helpers.stacks import award_stack, log_activity

focus_bp = Blueprint('focus', __name__)


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated


@focus_bp.route('/focus')
@login_required
def focus():
    return render_template('pages/focus.html', user=session)


@focus_bp.route('/api/save-focus', methods=['POST'])
@login_required
def save_focus():
    """
    Focus session DB mein save karo.
    Rule 8b: +1 Stack per completed Pomodoro session.
    """
    user_id          = session['user_id']
    task_name        = request.form.get('task', 'Study')
    sessions_count   = int(request.form.get('sessions', 1))
    duration_minutes = float(request.form.get('duration', 10))
    stacks_earned    = int(request.form.get('stacks', sessions_count))  # 1 per session

    mydb   = get_db_connection()
    cursor = mydb.cursor()

    # Always insert a new session record
    cursor.execute("""
        INSERT INTO focus (user_id, task_name, duration_minutes, sessions_count, stacks_earned)
        VALUES (%s, %s, %s, %s, %s)
    """, (user_id, task_name, duration_minutes, sessions_count, stacks_earned))

    mydb.commit()
    cursor.close()
    mydb.close()

    # Award stacks for each completed pomodoro session (Rule 8b)
    result = award_stack(user_id, 'pomodoro_done', stacks_earned)
    log_activity(user_id, 'focus', f'Completed {sessions_count} Pomodoro session(s) — {task_name}')

    session['stacks'] = result.get('new_total', session.get('stacks', 0))

    return jsonify({
        "success":      True,
        "message":      "Session saved!",
        "stacks_given": stacks_earned,
        "new_stacks":   result.get('new_total', 0)
    })


@focus_bp.route('/api/get-focus-stats')
@login_required
def get_focus_stats():
    """User ke total focus stats fetch karo."""
    user_id = session['user_id']
    mydb    = get_db_connection()
    cursor  = mydb.cursor()

    cursor.execute("""
        SELECT COALESCE(SUM(duration_minutes),0),
               COALESCE(SUM(sessions_count),0),
               COALESCE(SUM(stacks_earned),0)
        FROM focus WHERE user_id=%s
    """, (user_id,))
    row = cursor.fetchone()

    # Also get user's total stacks from users table
    cursor.execute("SELECT stacks, streak FROM users WHERE user_id=%s", (user_id,))
    user_row = cursor.fetchone()
    cursor.close()
    mydb.close()

    return jsonify({
        'total_minutes':  float(row[0]) if row else 0,
        'total_sessions': int(row[1])   if row else 0,
        'session_stacks': int(row[2])   if row else 0,
        'total_stacks':   int(user_row[0]) if user_row else 0,
        'streak':         int(user_row[1]) if user_row else 0
    })
