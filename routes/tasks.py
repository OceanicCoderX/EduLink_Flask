# ============================================================
# routes/tasks.py — Tasks Page + CRUD APIs
# Updated: awards +1 Stack on task completion
# ============================================================

from flask import Blueprint, render_template, request, session, redirect, url_for, jsonify
from db import get_db_connection
from datetime import date, timedelta, datetime
from functools import wraps
from helpers.stacks import award_stack, log_activity

tasks_bp = Blueprint('tasks', __name__)


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated


@tasks_bp.route('/tasks')
@login_required
def tasks():
    return render_template('pages/tasks.html', user=session)


# ── GET all tasks ────────────────────────────────────────────

@tasks_bp.route('/api/tasks', methods=['GET'])
@login_required
def get_tasks():
    """Logged-in user ke saare tasks fetch karo."""
    user_id = session['user_id']
    mydb    = get_db_connection()
    cursor  = mydb.cursor()

    try:
        cursor.execute(
            """SELECT task_id, user_id, task_title, task_description,
                      due_date, due_time, recurring, priority, status, created_date, completed_date
               FROM tasks WHERE user_id=%s
               ORDER BY due_date ASC, due_time ASC""",
            (user_id,)
        )
        rows = cursor.fetchall()
        cursor.close()
        mydb.close()

        task_list = [{
            'task_id':     t[0],
            'user_id':     t[1],
            'title':       t[2] or '',
            'description': t[3] if t[3] and t[3] != 'None' else '',
            'date':        str(t[4]) if t[4] else '',
            'time':        str(t[5]) if t[5] else '',
            'recurring':   t[6] or 'once',
            'priority':    t[7] if t[7] and t[7] != 'None' else 'medium',
            'status':      t[8] or 'pending',
            'createdAt':   str(t[9]) if t[9] else '',
            'completedDate': str(t[10]) if t[10] and str(t[10]) != '0000-00-00' else ''
        } for t in rows]

        return jsonify(task_list)

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify([])


# ── Save Task ────────────────────────────────────────────────

@tasks_bp.route('/api/save-task', methods=['POST'])
@login_required
def save_task():
    """Naya task save karo."""
    user_id          = session['user_id']
    task_title       = request.form.get('taskTitle')
    task_description = request.form.get('taskDescription', '')
    due_date         = request.form.get('taskDate')
    due_time         = request.form.get('taskTime')
    recurring        = request.form.get('taskRecurring', 'once')
    priority         = request.form.get('taskPriority', 'medium')
    created_date     = date.today()

    mydb   = get_db_connection()
    cursor = mydb.cursor()

    cursor.execute("""
        INSERT INTO tasks
        (user_id, task_title, task_description, due_date, due_time, recurring, priority, status, created_date)
        VALUES (%s, %s, %s, %s, %s, %s, %s, 'pending', %s)
    """, (user_id, task_title, task_description, due_date, due_time, recurring, priority, created_date))

    mydb.commit()
    task_id = cursor.lastrowid
    cursor.close()
    mydb.close()

    log_activity(user_id, 'task', f'Created task "{task_title}"')
    return jsonify({"success": True, "task_id": task_id, "message": "Task saved!"})


# ── Update Status (Complete/Pending) ─────────────────────────

@tasks_bp.route('/api/update-task-status', methods=['POST'])
@login_required
def update_task_status():
    """Task ka status complete/pending toggle karo. +1 Stack on complete."""
    task_id    = request.form.get('task_id')
    new_status = request.form.get('status')
    user_id    = session['user_id']

    mydb   = get_db_connection()
    cursor = mydb.cursor()

    # Get task title for activity log
    cursor.execute("SELECT task_title FROM tasks WHERE task_id=%s AND user_id=%s", (task_id, user_id))
    row = cursor.fetchone()
    task_title = row[0] if row else 'Task'

    if new_status == 'completed':
        # Get task details for cloning if recurring
        cursor.execute(
            "SELECT task_title, task_description, due_date, due_time, recurring, priority FROM tasks WHERE task_id=%s AND user_id=%s",
            (task_id, user_id)
        )
        task_data = cursor.fetchone()

        # Update current task: Set to 'once' to preserve history, mark as completed
        cursor.execute(
            "UPDATE tasks SET status='completed', completed_date=CURDATE(), recurring='once' WHERE task_id=%s AND user_id=%s",
            (task_id, user_id)
        )

        # If it was recurring, create a NEW pending task for the next occurrence
        if task_data and task_data[4] and task_data[4] != 'once':
            title, desc, d_date, d_time, rec, prio = task_data
            
            # Calculate next date (must be after today)
            today = date.today()
            base_date = d_date if d_date >= today else today
            
            if rec == 'daily':
                next_date = base_date + timedelta(days=1)
            elif rec == 'weekly':
                next_date = base_date + timedelta(weeks=1)
            elif rec == 'monthly':
                try:
                    month = base_date.month % 12 + 1
                    year = base_date.year + (base_date.month // 12)
                    next_date = base_date.replace(year=year, month=month)
                except ValueError:
                    next_date = base_date + timedelta(days=31)
                    next_date = next_date.replace(day=1) - timedelta(days=1)
            elif rec == 'yearly':
                try:
                    next_date = base_date.replace(year=base_date.year + 1)
                except ValueError:
                    next_date = base_date.replace(year=base_date.year + 1, month=3, day=1)
            else:
                next_date = base_date # Fallback

            cursor.execute("""
                INSERT INTO tasks
                (user_id, task_title, task_description, due_date, due_time, recurring, priority, status, created_date)
                VALUES (%s, %s, %s, %s, %s, %s, %s, 'pending', CURDATE())
            """, (user_id, title, desc, next_date, d_time, rec, prio))

        mydb.commit()
        cursor.close()
        mydb.close()

        # Award +1 Stack
        result = award_stack(user_id, 'task_complete', 1)
        log_activity(user_id, 'task', f'Completed task "{task_title}"')
        session['stacks'] = result.get('new_total', session.get('stacks', 0))

        return jsonify({
            "success":   True,
            "stack_awarded": True,
            "new_stacks": result.get('new_total', 0)
        })
    else:
        cursor.execute(
            "UPDATE tasks SET status='pending', completed_date='0000-00-00' WHERE task_id=%s AND user_id=%s",
            (task_id, user_id)
        )
        mydb.commit()
        cursor.close()
        mydb.close()
        return jsonify({"success": True, "stack_awarded": False})


# ── Edit Task ────────────────────────────────────────────────

@tasks_bp.route('/api/update-task', methods=['POST'])
@login_required
def update_task():
    """Existing task edit karo."""
    user_id          = session['user_id']
    task_id          = request.form.get('task_id')
    task_title       = request.form.get('taskTitle')
    task_description = request.form.get('taskDescription', '')
    due_date         = request.form.get('taskDate')
    due_time         = request.form.get('taskTime')
    recurring        = request.form.get('taskRecurring', 'once')
    priority         = request.form.get('taskPriority', 'medium')

    mydb   = get_db_connection()
    cursor = mydb.cursor()

    cursor.execute("""
        UPDATE tasks
        SET task_title=%s, task_description=%s, due_date=%s,
            due_time=%s, recurring=%s, priority=%s
        WHERE task_id=%s AND user_id=%s
    """, (task_title, task_description, due_date, due_time, recurring, priority, task_id, user_id))

    mydb.commit()
    cursor.close()
    mydb.close()

    return jsonify({"success": True})


# ── Delete Task ──────────────────────────────────────────────

@tasks_bp.route('/api/delete-task', methods=['POST'])
@login_required
def delete_task():
    """Task delete karo."""
    task_id = request.form.get('task_id')
    user_id = session['user_id']

    mydb   = get_db_connection()
    cursor = mydb.cursor()
    cursor.execute("DELETE FROM tasks WHERE task_id=%s AND user_id=%s", (task_id, user_id))
    mydb.commit()
    cursor.close()
    mydb.close()

    return jsonify({"success": True})


# ── Stack Award (Focus interval ping from JS) ────────────────

@tasks_bp.route('/api/award-focus-interval', methods=['POST'])
@login_required
def award_focus_interval():
    """
    JS se har 10 minute par call hota hai.
    Rule 8a: +1 Stack per 10 minutes of continuous activity.
    """
    user_id = session['user_id']
    
    # Rule 8a: Record 10 mins in focus table
    mydb   = get_db_connection()
    cursor = mydb.cursor()
    cursor.execute("""
        INSERT INTO focus (user_id, task_name, duration_minutes, sessions_count, stacks_earned)
        VALUES (%s, 'General Study (Auto-tracked)', 10, 0, 1)
    """, (user_id,))
    mydb.commit()
    cursor.close()
    mydb.close()

    result  = award_stack(user_id, 'focus_interval', 1)
    session['stacks'] = result.get('new_total', session.get('stacks', 0))
    return jsonify(result)
