# ============================================================
# routes/dashboard.py — Dashboard Page + Stats API
# ============================================================

from flask import Blueprint, render_template, session, redirect, url_for, jsonify
from db import get_db_connection

dashboard_bp = Blueprint('dashboard', __name__)


def login_required(f):
    """Simple decorator — login check karo."""
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated


@dashboard_bp.route('/dashboard')
@login_required
def dashboard():
    """Dashboard page render karo."""
    return render_template('pages/dashboard.html', user=session)


@dashboard_bp.route('/api/dashboard-stats')
@login_required
def dashboard_stats():
    """
    Dashboard ke liye live stats fetch karo DB se.
    JavaScript yahan se data lega.
    """
    user_id = session['user_id']
    mydb    = get_db_connection()
    cursor  = mydb.cursor()

    # Total tasks
    cursor.execute("SELECT COUNT(*) FROM tasks WHERE user_id=%s", (user_id,))
    total_tasks = cursor.fetchone()[0]

    # Completed tasks
    cursor.execute("SELECT COUNT(*) FROM tasks WHERE user_id=%s AND status='completed'", (user_id,))
    completed_tasks = cursor.fetchone()[0]

    # Total focus sessions
    cursor.execute("SELECT COUNT(*), COALESCE(SUM(duration_minutes),0), COALESCE(SUM(stacks_earned),0) FROM focus WHERE user_id=%s", (user_id,))
    focus_row = cursor.fetchone()
    total_sessions    = focus_row[0]
    total_minutes     = focus_row[1]
    total_stacks      = focus_row[2]

    # Recent tasks (last 4)
    cursor.execute(
        "SELECT task_title, status, priority, due_date FROM tasks WHERE user_id=%s ORDER BY created_date DESC LIMIT 4",
        (user_id,)
    )
    recent_tasks = [
        {'title': r[0], 'status': r[1], 'priority': r[2], 'due_date': str(r[3])}
        for r in cursor.fetchall()
    ]

    # Recent notes (last 4)
    cursor.execute(
        "SELECT notes_title, category, created_date FROM notes WHERE user_id=%s ORDER BY created_date DESC LIMIT 4",
        (user_id,)
    )
    recent_notes = [
        {'title': r[0], 'category': r[1], 'date': str(r[2])}
        for r in cursor.fetchall()
    ]

    cursor.close()
    mydb.close()

    return jsonify({
        'total_tasks': total_tasks,
        'completed_tasks': completed_tasks,
        'total_sessions': total_sessions,
        'total_hours': round(total_minutes / 60, 1),
        'total_stacks': total_stacks,
        'recent_tasks': recent_tasks,
        'recent_notes': recent_notes
    })
