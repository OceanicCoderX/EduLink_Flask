# ============================================================
# routes/dashboard.py — Dashboard Page + Stats API
# Updated: pulls stacks from users.stacks (centralized)
# ============================================================

from flask import Blueprint, render_template, session, redirect, url_for, jsonify
from db import get_db_connection
from functools import wraps

dashboard_bp = Blueprint('dashboard', __name__)


def login_required(f):
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
    return render_template('pages/dashboard.html', user=session)


@dashboard_bp.route('/api/dashboard-stats')
@login_required
def dashboard_stats():
    user_id = session['user_id']
    mydb    = get_db_connection()
    cursor  = mydb.cursor()

    # Total tasks
    cursor.execute("SELECT COUNT(*) FROM tasks WHERE user_id=%s", (user_id,))
    total_tasks = cursor.fetchone()[0]

    # Completed tasks
    cursor.execute("SELECT COUNT(*) FROM tasks WHERE user_id=%s AND status='completed'", (user_id,))
    completed_tasks = cursor.fetchone()[0]

    # Focus stats
    cursor.execute("""
        SELECT COUNT(*), COALESCE(SUM(duration_minutes),0), COALESCE(SUM(sessions_count),0)
        FROM focus WHERE user_id=%s
    """, (user_id,))
    focus_row      = cursor.fetchone()
    total_sessions = focus_row[0]
    total_minutes  = focus_row[1]

    # Centralized stacks & streak from users table
    cursor.execute("SELECT stacks, streak FROM users WHERE user_id=%s", (user_id,))
    user_row     = cursor.fetchone()
    total_stacks = int(user_row[0]) if user_row else 0
    streak       = int(user_row[1]) if user_row else 0

    # Update session with latest stacks
    session['stacks'] = total_stacks
    session['streak'] = streak

    # Recent tasks (last 4)
    cursor.execute("""
        SELECT task_title, status, priority, due_date
        FROM tasks WHERE user_id=%s ORDER BY created_date DESC LIMIT 4
    """, (user_id,))
    recent_tasks = [
        {'title': r[0], 'status': r[1], 'priority': r[2], 'due_date': str(r[3])}
        for r in cursor.fetchall()
    ]

    # Recent notes (last 4)
    cursor.execute("""
        SELECT notes_title, category, created_date
        FROM notes WHERE user_id=%s ORDER BY created_date DESC LIMIT 4
    """, (user_id,))
    recent_notes = [
        {'title': r[0], 'category': r[1], 'date': str(r[2])}
        for r in cursor.fetchall()
    ]

    # Recent activity (last 5)
    cursor.execute("""
        SELECT action_type, action_desc, created_at
        FROM activity_log WHERE user_id=%s ORDER BY created_at DESC LIMIT 5
    """, (user_id,))
    recent_activity = [
        {'type': r[0], 'desc': r[1], 'time': r[2].strftime("%b %d, %I:%M %p") if r[2] else ''}
        for r in cursor.fetchall()
    ]

    # Uploaded files count
    cursor.execute("SELECT COUNT(*) FROM uploaded_files WHERE user_id=%s", (user_id,))
    total_files = cursor.fetchone()[0]

    cursor.close()
    mydb.close()

    return jsonify({
        'total_tasks':      total_tasks,
        'completed_tasks':  completed_tasks,
        'total_sessions':   total_sessions,
        'total_hours':      round(float(total_minutes) / 60, 1),
        'total_stacks':     total_stacks,
        'streak':           streak,
        'total_files':      total_files,
        'recent_tasks':     recent_tasks,
        'recent_notes':     recent_notes,
        'recent_activity':  recent_activity
    })
