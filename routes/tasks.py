# ============================================================
# routes/tasks.py — Tasks Page + CRUD APIs
# ============================================================

from flask import Blueprint, render_template, request, session, redirect, url_for, jsonify
from db import get_db_connection
from datetime import date
from functools import wraps

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


# Insert Task

@tasks_bp.route('/api/tasks', methods=['GET'])
@login_required
def get_tasks():
    """Logged-in user ke saare tasks fetch karo."""
    user_id = session['user_id']
    mydb    = get_db_connection()
    cursor  = mydb.cursor()

    cursor.execute(
        "SELECT task_id, user_id, task_title, task_description, due_date, due_time, recurring, priority, status, created_date FROM tasks WHERE user_id=%s ORDER BY due_date ASC, due_time ASC",
        (user_id,)
    )
    rows = cursor.fetchall()
    cursor.close()
    mydb.close()

    task_list = []
    for t in rows:
        task_list.append({
            'task_id':     t[0],
            'user_id':     t[1],
            'title':       t[2] or '',
            'description': t[3] if t[3] and t[3] != 'None' else '',
            'date':        str(t[4]) if t[4] else '',
            'time':        str(t[5]) if t[5] else '',
            'recurring':   t[6] or 'once',
            'priority':    t[7] if t[7] and t[7] != 'None' else 'medium',
            'status':      t[8] or 'pending',
            'createdAt':   str(t[9]) if t[9] else ''
        })

    return jsonify(task_list)

# Save Task

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
    status           = 'pending'
    created_date     = date.today()

    mydb   = get_db_connection()
    cursor = mydb.cursor()

    query = """
        INSERT INTO tasks
        (user_id, task_title, task_description, due_date, due_time, recurring, priority, status, created_date)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    cursor.execute(query, (user_id, task_title, task_description, due_date, due_time, recurring, priority, status, created_date))
    mydb.commit()
    task_id = cursor.lastrowid
    cursor.close()
    mydb.close()

    return jsonify({"success": True, "task_id": task_id, "message": "Task saved!"})

# Upadate task

@tasks_bp.route('/api/update-task-status', methods=['POST'])
@login_required
def update_task_status():
    """Task ka status complete/pending toggle karo."""
    task_id    = request.form.get('task_id')
    new_status = request.form.get('status')
    user_id    = session['user_id']

    mydb   = get_db_connection()
    cursor = mydb.cursor()

    if new_status == 'completed':
        cursor.execute(
            "UPDATE tasks SET status='completed', completed_date=CURDATE() WHERE task_id=%s AND user_id=%s",
            (task_id, user_id)
        )
    else:
        cursor.execute(
            "UPDATE tasks SET status='pending', completed_date='0000-00-00' WHERE task_id=%s AND user_id=%s",
            (task_id, user_id)
        )

    mydb.commit()
    cursor.close()
    mydb.close()

    return jsonify({"success": True})



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
        SET task_title=%s, task_description=%s, due_date=%s, due_time=%s,
            recurring=%s, priority=%s
        WHERE task_id=%s AND user_id=%s
    """, (task_title, task_description, due_date, due_time, recurring, priority, task_id, user_id))

    mydb.commit()
    cursor.close()
    mydb.close()

    return jsonify({"success": True})


# Delete task

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
