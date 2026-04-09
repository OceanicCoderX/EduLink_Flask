# ============================================================
# routes/classroom.py — Classroom + Study Rooms API
# Updated: +1 Stack on room create, collaborative notes save
# ============================================================

from flask import Blueprint, render_template, request, session, redirect, url_for, jsonify
from db import get_db_connection
from datetime import date
from functools import wraps
from helpers.stacks import award_stack, log_activity

classroom_bp = Blueprint('classroom', __name__)


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated


# ── Pages ───────────────────────────────────────────────────

@classroom_bp.route('/classroom')
@login_required
def classroom():
    return render_template('pages/classroom.html', user=session)


@classroom_bp.route('/room/<int:room_id>')
@login_required
def room(room_id):
    user_id = session['user_id']
    mydb    = get_db_connection()
    cursor  = mydb.cursor()

    cursor.execute("SELECT * FROM classroom WHERE room_id=%s", (room_id,))
    room_data = cursor.fetchone()

    if not room_data:
        cursor.close(); mydb.close()
        return redirect(url_for('classroom.classroom'))

    is_admin  = (room_data[3] == user_id)

    cursor.execute(
        "SELECT member_id FROM room_members WHERE room_id=%s AND member_id=%s",
        (room_id, user_id)
    )
    is_member = cursor.fetchone() is not None

    if not is_admin and not is_member:
        cursor.close(); mydb.close()
        return redirect(url_for('classroom.classroom'))

    # Room members
    cursor.execute("""
        SELECT u.user_id, u.profilename, u.profile_pic, u.profession
        FROM room_members rm
        JOIN users u ON u.user_id = rm.member_id
        WHERE rm.room_id=%s
    """, (room_id,))
    members = [{'user_id': r[0], 'name': r[1], 'pic': r[2], 'profession': r[3] if r[3] else 'Student'}
               for r in cursor.fetchall()]

    # Last 50 messages
    cursor.execute("""
        SELECT cm.message, cm.sent_at, u.profilename, u.user_id, u.profession
        FROM classroom_messages cm
        JOIN users u ON u.user_id = cm.user_id
        WHERE cm.room_id=%s
        ORDER BY cm.sent_at ASC LIMIT 50
    """, (room_id,))
    messages = [
        {'message': r[0], 'time': r[1].strftime("%I:%M %p"),
         'username': r[2], 'user_id': r[3], 'profession': r[4] if r[4] else 'Student'}
        for r in cursor.fetchall()
    ]

    cursor.close(); mydb.close()

    # subject is index 5, room_notes is index 6 (after migration adds room_notes)
    room_dict = {
        'room_id':          room_data[0],
        'room_name':        room_data[1],
        'room_description': room_data[2],
        'admin_id':         room_data[3],
        'subject':          room_data[5] if len(room_data) > 5 else 'General',
        'room_notes':       room_data[6] if len(room_data) > 6 else ''
    }

    return render_template('pages/room.html',
                           user=session, room=room_dict,
                           members=members, messages=messages,
                           is_admin=is_admin)


# ── APIs ────────────────────────────────────────────────────

@classroom_bp.route('/api/create-room', methods=['POST'])
@login_required
def create_room():
    """Naya study room banao. Rule 8d: +1 Stack for creating a room."""
    user_id     = session['user_id']
    room_name   = request.form.get('room_name')
    description = request.form.get('room_description', '')
    subject     = request.form.get('subject', 'General')
    today       = date.today()

    mydb   = get_db_connection()
    cursor = mydb.cursor()

    cursor.execute("""
        INSERT INTO classroom (room_name, room_description, admin_id, created_date, total_duration, subject)
        VALUES (%s, %s, %s, %s, '0h', %s)
    """, (room_name, description, user_id, today, subject))

    mydb.commit()
    room_id = cursor.lastrowid
    cursor.close()
    mydb.close()

    # Award stack + log
    result = award_stack(user_id, 'room_created', 1)
    log_activity(user_id, 'room', f'Created room "{room_name}"')
    session['stacks'] = result.get('new_total', session.get('stacks', 0))

    return jsonify({"success": True, "room_id": room_id, "new_stacks": result.get('new_total', 0)})


@classroom_bp.route('/api/get-my-rooms')
@login_required
def get_my_rooms():
    user_id = session['user_id']
    mydb    = get_db_connection()
    cursor  = mydb.cursor()

    cursor.execute(
        "SELECT room_id, room_name, room_description, created_date, subject FROM classroom WHERE admin_id=%s ORDER BY created_date DESC",
        (user_id,)
    )
    rows = cursor.fetchall()
    cursor.close(); mydb.close()

    return jsonify([
        {'room_id': r[0], 'room_name': r[1], 'description': r[2],
         'created_date': str(r[3]), 'subject': r[4] or 'General'}
        for r in rows
    ])


@classroom_bp.route('/api/get-joined-rooms')
@login_required
def get_joined_rooms():
    user_id = session['user_id']
    mydb    = get_db_connection()
    cursor  = mydb.cursor()

    cursor.execute("""
        SELECT c.room_id, c.room_name, c.room_description, rm.join_date, c.subject
        FROM room_members rm
        JOIN classroom c ON c.room_id = rm.room_id
        WHERE rm.member_id=%s ORDER BY rm.join_date DESC
    """, (user_id,))
    rows = cursor.fetchall()
    cursor.close(); mydb.close()

    return jsonify([
        {'room_id': r[0], 'room_name': r[1], 'description': r[2],
         'join_date': str(r[3]), 'subject': r[4] or 'General'}
        for r in rows
    ])


@classroom_bp.route('/api/join-room', methods=['POST'])
@login_required
def join_room_api():
    user_id = session['user_id']
    room_id = request.form.get('room_id')
    today   = date.today()

    mydb   = get_db_connection()
    cursor = mydb.cursor()

    cursor.execute(
        "SELECT member_id FROM room_members WHERE room_id=%s AND member_id=%s",
        (room_id, user_id)
    )
    if cursor.fetchone():
        cursor.close(); mydb.close()
        return jsonify({"success": True, "message": "Already a member"})

    cursor.execute(
        "INSERT INTO room_members (member_id, room_id, join_date) VALUES (%s, %s, %s)",
        (user_id, room_id, today)
    )
    mydb.commit()
    cursor.close(); mydb.close()

    return jsonify({"success": True, "message": "Joined room!"})


@classroom_bp.route('/api/delete-room', methods=['POST'])
@login_required
def delete_room():
    user_id = session['user_id']
    room_id = request.form.get('room_id')

    mydb   = get_db_connection()
    cursor = mydb.cursor()

    cursor.execute("SELECT admin_id FROM classroom WHERE room_id=%s", (room_id,))
    row = cursor.fetchone()
    if not row or row[0] != user_id:
        cursor.close(); mydb.close()
        return jsonify({"success": False, "error": "Not authorized"})

    cursor.execute("DELETE FROM room_members WHERE room_id=%s", (room_id,))
    cursor.execute("DELETE FROM classroom_messages WHERE room_id=%s", (room_id,))
    cursor.execute("DELETE FROM classroom WHERE room_id=%s", (room_id,))
    mydb.commit()
    cursor.close(); mydb.close()

    return jsonify({"success": True})


@classroom_bp.route('/api/remove-room-member', methods=['POST'])
@login_required
def remove_room_member():
    user_id   = session['user_id']
    room_id   = request.form.get('room_id')
    member_id = request.form.get('member_id')

    mydb   = get_db_connection()
    cursor = mydb.cursor()

    cursor.execute("SELECT admin_id FROM classroom WHERE room_id=%s", (room_id,))
    row = cursor.fetchone()
    if not row or row[0] != user_id:
        cursor.close(); mydb.close()
        return jsonify({"success": False, "error": "Not authorized"})

    cursor.execute(
        "DELETE FROM room_members WHERE room_id=%s AND member_id=%s",
        (room_id, member_id)
    )
    mydb.commit()
    cursor.close(); mydb.close()

    return jsonify({"success": True})


# ── Collaborative Notes ──────────────────────────────────────

@classroom_bp.route('/api/save-room-notes', methods=['POST'])
@login_required
def save_room_notes():
    """
    Save collaborative notes written during a video session.
    Rule 7: Auto-saves when user leaves, or manually via Save button.
    Rule 8: +1 Stack for saving notes.
    """
    user_id = session['user_id']
    room_id = request.form.get('room_id')
    notes   = request.form.get('notes', '')

    mydb   = get_db_connection()
    cursor = mydb.cursor()

    # Verify user is admin or member
    cursor.execute(
        "SELECT admin_id FROM classroom WHERE room_id=%s", (room_id,)
    )
    room = cursor.fetchone()
    if not room:
        cursor.close(); mydb.close()
        return jsonify({"success": False, "error": "Room not found"})

    cursor.execute(
        "UPDATE classroom SET room_notes=%s WHERE room_id=%s",
        (notes, room_id)
    )
    mydb.commit()
    cursor.close(); mydb.close()

    # Award +1 Stack for saving notes (Rule 8)
    result = award_stack(user_id, 'room_notes_saved', 1)
    log_activity(user_id, 'notes', f'Saved collaborative notes in room #{room_id}')
    session['stacks'] = result.get('new_total', session.get('stacks', 0))

    return jsonify({
        "success":   True,
        "message":   "Notes saved!",
        "new_stacks": result.get('new_total', 0)
    })


@classroom_bp.route('/api/get-room-notes/<int:room_id>')
@login_required
def get_room_notes(room_id):
    """Get existing collaborative notes for a room."""
    mydb   = get_db_connection()
    cursor = mydb.cursor()
    cursor.execute("SELECT room_notes FROM classroom WHERE room_id=%s", (room_id,))
    row = cursor.fetchone()
    cursor.close(); mydb.close()

    return jsonify({"notes": row[0] if row and row[0] else ""})
