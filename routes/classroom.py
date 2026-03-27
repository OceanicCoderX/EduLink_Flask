# ============================================================
# routes/classroom.py — Classroom Page + Study Rooms API
# ============================================================

from flask import Blueprint, render_template, request, session, redirect, url_for, jsonify
from db import get_db_connection
from datetime import date
from functools import wraps

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
    """Classroom main page."""
    return render_template('pages/classroom.html', user=session)


@classroom_bp.route('/room/<int:room_id>')
@login_required
def room(room_id):
    """
    Specific study room page — yahan text chat + video hoga.
    Pehle check karo ki user is room ka member hai ya nahi.
    """
    user_id = session['user_id']
    mydb    = get_db_connection()
    cursor  = mydb.cursor()

    # Room ki info fetch karo
    cursor.execute("SELECT * FROM classroom WHERE room_id=%s", (room_id,))
    room_data = cursor.fetchone()

    if not room_data:
        cursor.close()
        mydb.close()
        return redirect(url_for('classroom.classroom'))

    # Check: user is room ka admin hai ya member
    is_admin = (room_data[3] == user_id)  # admin_id == user_id

    cursor.execute(
        "SELECT member_id FROM room_members WHERE room_id=%s AND member_id=%s",
        (room_id, user_id)
    )
    is_member = cursor.fetchone() is not None

    # Agar na admin na member — access deny
    if not is_admin and not is_member:
        cursor.close()
        mydb.close()
        return redirect(url_for('classroom.classroom'))

    # Room members ki list
    cursor.execute("""
        SELECT u.user_id, u.profilename, u.profile_pic
        FROM room_members rm
        JOIN users u ON u.user_id = rm.member_id
        WHERE rm.room_id=%s
    """, (room_id,))
    members = [{'user_id': r[0], 'name': r[1], 'pic': r[2]} for r in cursor.fetchall()]

    # Last 50 messages load karo
    cursor.execute("""
        SELECT cm.message, cm.sent_at, u.profilename, u.user_id
        FROM classroom_messages cm
        JOIN users u ON u.user_id = cm.user_id
        WHERE cm.room_id=%s
        ORDER BY cm.sent_at ASC
        LIMIT 50
    """, (room_id,))
    messages = [
        {'message': r[0], 'time': r[1].strftime("%I:%M %p"), 'username': r[2], 'user_id': r[3]}
        for r in cursor.fetchall()
    ]

    cursor.close()
    mydb.close()

    room_dict = {
        'room_id':          room_data[0],
        'room_name':        room_data[1],
        'room_description': room_data[2],
        'admin_id':         room_data[3],
        'subject':          room_data[5] if len(room_data) > 5 else 'General'
    }

    return render_template('pages/room.html',
                           user=session,
                           room=room_dict,
                           members=members,
                           messages=messages,
                           is_admin=is_admin)


# ── APIs ────────────────────────────────────────────────────

@classroom_bp.route('/api/create-room', methods=['POST'])
@login_required
def create_room():
    """Naya study room banao."""
    user_id     = session['user_id']
    room_name   = request.form.get('room_name')
    description = request.form.get('room_description', '')
    subject     = request.form.get('subject', 'General')
    today       = date.today()

    mydb   = get_db_connection()
    cursor = mydb.cursor()

    cursor.execute("""
        INSERT INTO classroom (room_name, room_description, admin_id, created_date, total_duration, subject)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (room_name, description, user_id, today, '0h', subject))

    mydb.commit()
    room_id = cursor.lastrowid
    cursor.close()
    mydb.close()

    return jsonify({"success": True, "room_id": room_id})


@classroom_bp.route('/api/get-my-rooms')
@login_required
def get_my_rooms():
    """User ke created rooms fetch karo."""
    user_id = session['user_id']
    mydb    = get_db_connection()
    cursor  = mydb.cursor()

    cursor.execute(
        "SELECT room_id, room_name, room_description, created_date, subject FROM classroom WHERE admin_id=%s ORDER BY created_date DESC",
        (user_id,)
    )
    rows = cursor.fetchall()
    cursor.close()
    mydb.close()

    rooms = [
        {'room_id': r[0], 'room_name': r[1], 'description': r[2], 'created_date': str(r[3]), 'subject': r[4] if r[4] else 'General'}
        for r in rows
    ]
    return jsonify(rooms)


@classroom_bp.route('/api/get-joined-rooms')
@login_required
def get_joined_rooms():
    """User ke joined rooms fetch karo."""
    user_id = session['user_id']
    mydb    = get_db_connection()
    cursor  = mydb.cursor()

    cursor.execute("""
        SELECT c.room_id, c.room_name, c.room_description, rm.join_date, c.subject
        FROM room_members rm
        JOIN classroom c ON c.room_id = rm.room_id
        WHERE rm.member_id=%s
        ORDER BY rm.join_date DESC
    """, (user_id,))
    rows = cursor.fetchall()
    cursor.close()
    mydb.close()

    rooms = [
        {'room_id': r[0], 'room_name': r[1], 'description': r[2], 'join_date': str(r[3]), 'subject': r[4] if r[4] else 'General'}
        for r in rows
    ]
    return jsonify(rooms)


@classroom_bp.route('/api/join-room', methods=['POST'])
@login_required
def join_room_api():
    """Room join karo (member ban jao)."""
    user_id = session['user_id']
    room_id = request.form.get('room_id')
    today   = date.today()

    mydb   = get_db_connection()
    cursor = mydb.cursor()

    # Already member hai?
    cursor.execute(
        "SELECT member_id FROM room_members WHERE room_id=%s AND member_id=%s",
        (room_id, user_id)
    )
    if cursor.fetchone():
        cursor.close()
        mydb.close()
        return jsonify({"success": True, "message": "Already a member"})

    cursor.execute(
        "INSERT INTO room_members (member_id, room_id, join_date) VALUES (%s, %s, %s)",
        (user_id, room_id, today)
    )
    mydb.commit()
    cursor.close()
    mydb.close()

    return jsonify({"success": True, "message": "Joined room!"})


@classroom_bp.route('/api/delete-room', methods=['POST'])
@login_required
def delete_room():
    """Room delete karo (sirf admin kar sakta hai)."""
    user_id = session['user_id']
    room_id = request.form.get('room_id')

    mydb   = get_db_connection()
    cursor = mydb.cursor()

    # Verify admin
    cursor.execute("SELECT admin_id FROM classroom WHERE room_id=%s", (room_id,))
    row = cursor.fetchone()
    if not row or row[0] != user_id:
        cursor.close()
        mydb.close()
        return jsonify({"success": False, "error": "Not authorized"})

    cursor.execute("DELETE FROM room_members WHERE room_id=%s", (room_id,))
    cursor.execute("DELETE FROM classroom_messages WHERE room_id=%s", (room_id,))
    cursor.execute("DELETE FROM classroom WHERE room_id=%s", (room_id,))
    mydb.commit()
    cursor.close()
    mydb.close()

    return jsonify({"success": True})


@classroom_bp.route('/api/remove-room-member', methods=['POST'])
@login_required
def remove_room_member():
    """Admin kisi member ko room se hataye."""
    user_id    = session['user_id']
    room_id    = request.form.get('room_id')
    member_id  = request.form.get('member_id')

    mydb   = get_db_connection()
    cursor = mydb.cursor()

    # Sirf admin kar sakta hai
    cursor.execute("SELECT admin_id FROM classroom WHERE room_id=%s", (room_id,))
    row = cursor.fetchone()
    if not row or row[0] != user_id:
        cursor.close()
        mydb.close()
        return jsonify({"success": False, "error": "Not authorized"})

    cursor.execute(
        "DELETE FROM room_members WHERE room_id=%s AND member_id=%s",
        (room_id, member_id)
    )
    mydb.commit()
    cursor.close()
    mydb.close()

    return jsonify({"success": True})
