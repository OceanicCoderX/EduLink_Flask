# ============================================================
# routes/focus.py — Focus Timer Page + Save Session
# ============================================================

from flask import Blueprint, render_template, request, session, redirect, url_for, jsonify
from db import get_db_connection
from functools import wraps

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
    Agar user ka existing record hai toh update, nahi toh insert.
    """
    user_id          = session['user_id']
    task_name        = request.form.get('task', 'Study')
    sessions_count   = int(request.form.get('sessions', 1))
    duration_minutes = float(request.form.get('duration', 10))
    stacks_earned    = int(request.form.get('stacks', 1))

    mydb   = get_db_connection()
    cursor = mydb.cursor()

    # Check if record exists
    cursor.execute("SELECT focus_id FROM focus WHERE user_id=%s ORDER BY session_date DESC LIMIT 1", (user_id,))
    existing = cursor.fetchone()

    if existing:
        cursor.execute("""
            UPDATE focus
            SET task_name=%s, duration_minutes=duration_minutes+%s, sessions_count=sessions_count+%s, stacks_earned=stacks_earned+%s
            WHERE user_id=%s ORDER BY session_date DESC LIMIT 1
        """, (task_name, duration_minutes, sessions_count, stacks_earned, user_id))
    else:
        cursor.execute("""
            INSERT INTO focus (user_id, task_name, duration_minutes, sessions_count, stacks_earned)
            VALUES (%s, %s, %s, %s, %s)
        """, (user_id, task_name, duration_minutes, sessions_count, stacks_earned))

    mydb.commit()
    cursor.close()
    mydb.close()

    return jsonify({"success": True, "message": "Session saved!"})


@focus_bp.route('/api/get-focus-stats')
@login_required
def get_focus_stats():
    """User ke total focus stats fetch karo."""
    user_id = session['user_id']
    mydb    = get_db_connection()
    cursor  = mydb.cursor()

    cursor.execute("""
        SELECT COALESCE(SUM(duration_minutes),0), COALESCE(SUM(sessions_count),0), COALESCE(SUM(stacks_earned),0)
        FROM focus WHERE user_id=%s
    """, (user_id,))
    row = cursor.fetchone()
    cursor.close()
    mydb.close()

    return jsonify({
    'total_minutes':   row[0],
    'total_sessions':  row[1],
    'total_stacks':    row[2]
})
