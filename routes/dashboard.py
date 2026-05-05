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

    # Total website time spent (for Total Study Hours card)
    cursor.execute("SELECT COALESCE(SUM(total_minutes), 0) FROM daily_time_spent WHERE user_id=%s", (user_id,))
    total_website_minutes = cursor.fetchone()[0]

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

    # --- Chart Data ---
    
    # Total notes created
    cursor.execute("SELECT COUNT(*) FROM notes WHERE user_id=%s", (user_id,))
    total_notes = cursor.fetchone()[0]

    # Total classrooms joined
    cursor.execute("SELECT COUNT(*) FROM room_members WHERE member_id=%s", (user_id,))
    total_classrooms = cursor.fetchone()[0]

    # Total communities joined
    cursor.execute("SELECT COUNT(*) FROM group_members WHERE member_id=%s", (user_id,))
    total_communities = cursor.fetchone()[0]

    # Daily time spent (last 7 days)
    cursor.execute("""
        SELECT DATE(date) as cdate, SUM(total_minutes) as mins
        FROM daily_time_spent
        WHERE user_id=%s AND date >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
        GROUP BY DATE(date)
        ORDER BY DATE(date) ASC
    """, (user_id,))
    daily_time = [{'date': str(r[0]), 'minutes': int(r[1]) if r[1] else 0} for r in cursor.fetchall()]

    # Weekly time spent (last 4 weeks)
    cursor.execute("""
        SELECT CONCAT(YEAR(date), '-W', LPAD(WEEK(date), 2, '0')) as cdate, SUM(total_minutes) as mins
        FROM daily_time_spent
        WHERE user_id=%s AND date >= DATE_SUB(CURDATE(), INTERVAL 4 WEEK)
        GROUP BY YEAR(date), WEEK(date)
        ORDER BY YEAR(date), WEEK(date) ASC
    """, (user_id,))
    weekly_time = [{'date': str(r[0]), 'minutes': int(r[1]) if r[1] else 0} for r in cursor.fetchall()]

    # Monthly time spent (last 12 months)
    cursor.execute("""
        SELECT DATE_FORMAT(date, '%Y-%m') as cdate, SUM(total_minutes) as mins
        FROM daily_time_spent
        WHERE user_id=%s AND date >= DATE_SUB(CURDATE(), INTERVAL 12 MONTH)
        GROUP BY DATE_FORMAT(date, '%Y-%m')
        ORDER BY DATE_FORMAT(date, '%Y-%m') ASC
    """, (user_id,))
    monthly_time = [{'date': str(r[0]), 'minutes': int(r[1]) if r[1] else 0} for r in cursor.fetchall()]

    cursor.close()
    mydb.close()

    return jsonify({
        'total_tasks':      total_tasks,
        'completed_tasks':  completed_tasks,
        'total_sessions':   total_sessions,
        'total_hours':      round(float(total_website_minutes) / 60, 1),
        'total_stacks':     total_stacks,
        'streak':           streak,
        'total_files':      total_files,
        'recent_tasks':     recent_tasks,
        'recent_notes':     recent_notes,
        'recent_activity':  recent_activity,
        'chart_data': {
            'pie': {
                'focus_minutes': total_minutes,
                'tasks_completed': completed_tasks,
                'notes_created': total_notes,
                'classrooms_joined': total_classrooms,
                'communities_joined': total_communities
            },
            'line': {
                'daily_time': daily_time,
                'weekly_time': weekly_time,
                'monthly_time': monthly_time
            }
        }
    })


from flask import request
@dashboard_bp.route('/api/progress-report')
@login_required
def progress_report():
    timeframe = request.args.get('range', 'weekly')
    user_id = session['user_id']
    mydb    = get_db_connection()
    cursor  = mydb.cursor()

    if timeframe == 'monthly':
        interval = '1 MONTH'
    else:
        interval = '7 DAY'

    # Focus time
    cursor.execute(f"SELECT COALESCE(SUM(duration_minutes), 0) FROM focus WHERE user_id=%s AND session_date >= DATE_SUB(CURDATE(), INTERVAL {interval})", (user_id,))
    focus_mins = cursor.fetchone()[0]

    # Completed tasks
    cursor.execute(f"SELECT task_title, DATE(completed_date) FROM tasks WHERE user_id=%s AND status='completed' AND completed_date >= DATE_SUB(CURDATE(), INTERVAL {interval}) ORDER BY completed_date DESC", (user_id,))
    tasks = [{'title': r[0], 'date': str(r[1])} for r in cursor.fetchall()]

    # Joined classrooms (using join_date from room_members)
    cursor.execute(f"SELECT c.room_name, rm.join_date FROM room_members rm JOIN classroom c ON rm.room_id = c.room_id WHERE rm.member_id=%s AND rm.join_date >= DATE_SUB(CURDATE(), INTERVAL {interval}) ORDER BY rm.join_date DESC", (user_id,))
    classrooms = [{'name': r[0], 'date': str(r[1])} for r in cursor.fetchall()]

    # Created notes
    cursor.execute(f"SELECT notes_title, created_date FROM notes WHERE user_id=%s AND created_date >= DATE_SUB(CURDATE(), INTERVAL {interval}) ORDER BY created_date DESC", (user_id,))
    notes = [{'title': r[0], 'date': str(r[1])} for r in cursor.fetchall()]

    # Joined communities (group_members has join_date)
    # Wait, does group_members have join_date? Yes, checked earlier.
    # We join community to get group_name.
    cursor.execute(f"SELECT c.group_name, gm.join_date FROM group_members gm JOIN community c ON gm.group_id = c.group_id WHERE gm.member_id=%s AND gm.join_date >= DATE_SUB(CURDATE(), INTERVAL {interval}) ORDER BY gm.join_date DESC", (user_id,))
    communities = [{'name': r[0], 'date': str(r[1])} for r in cursor.fetchall()]

    cursor.close()
    mydb.close()

    return jsonify({
        'range': timeframe,
        'focus_minutes': int(focus_mins) if focus_mins else 0,
        'tasks': tasks,
        'classrooms': classrooms,
        'notes': notes,
        'communities': communities
    })

@dashboard_bp.route('/api/track-time', methods=['POST'])
@login_required
def track_time():
    user_id = session['user_id']
    mydb = get_db_connection()
    cursor = mydb.cursor()
    
    cursor.execute("SELECT id FROM daily_time_spent WHERE user_id=%s AND date=CURDATE()", (user_id,))
    row = cursor.fetchone()
    
    if row:
        cursor.execute("UPDATE daily_time_spent SET total_minutes = total_minutes + 1 WHERE id=%s", (row[0],))
    else:
        cursor.execute("INSERT INTO daily_time_spent (user_id, date, total_minutes) VALUES (%s, CURDATE(), 1)", (user_id,))
        
    mydb.commit()
    cursor.close()
    mydb.close()
    
    return jsonify({'success': True})