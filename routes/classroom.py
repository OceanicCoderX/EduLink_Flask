# ============================================================
# routes/classroom.py — Complete Classroom + Study Rooms
# Fixes: password, status, session time, stacks on join,
#        close-room (admin), leave-room (member), notes
# ============================================================

from flask import Blueprint, render_template, request, session, redirect, url_for, jsonify
from db import get_db_connection
from datetime import date, datetime
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


# ── Pages ─────────────────────────────────────────────────────

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

    # Parse room columns (safe access by position)
    # 0:room_id, 1:room_name, 2:room_description, 3:admin_id,
    # 4:created_date, 5:total_duration, 6:subject, 7:room_notes,
    # 8:room_password, 9:status, 10:total_minutes
    room_status = room_data[9] if len(room_data) > 9 else 'active'

    # Closed room — redirect out
    if room_status == 'closed':
        cursor.close(); mydb.close()
        return redirect(url_for('classroom.classroom'))

    is_admin = (room_data[3] == user_id)

    # Check membership
    cursor.execute(
        "SELECT member_id FROM room_members WHERE room_id=%s AND member_id=%s",
        (room_id, user_id)
    )
    is_member = cursor.fetchone() is not None

    if not is_admin and not is_member:
        cursor.close(); mydb.close()
        return redirect(url_for('classroom.classroom'))

    # Update session join_time for time tracking
    if is_member:
        cursor.execute(
            "UPDATE room_members SET join_time=%s WHERE room_id=%s AND member_id=%s",
            (datetime.now(), room_id, user_id)
        )
        mydb.commit()

    # Room members list
    cursor.execute("""
        SELECT u.user_id, u.profilename, u.profile_pic, u.profession, u.avatar_id
        FROM room_members rm
        JOIN users u ON u.user_id = rm.member_id
        WHERE rm.room_id=%s
    """, (room_id,))
    members = [
        {
            'user_id':    r[0],
            'name':       r[1],
            'pic':        r[2],
            'profession': r[3] if r[3] else 'Student',
            'avatar_id':  r[4] if r[4] else 1
        }
        for r in cursor.fetchall()
    ]

    # Last 50 messages
    cursor.execute("""
        SELECT cm.message, cm.sent_at, u.profilename, u.user_id, u.profession
        FROM classroom_messages cm
        JOIN users u ON u.user_id = cm.user_id
        WHERE cm.room_id=%s
        ORDER BY cm.sent_at ASC LIMIT 50
    """, (room_id,))
    messages = [
        {
            'message':    r[0],
            'time':       r[1].strftime("%I:%M %p"),
            'username':   r[2],
            'user_id':    r[3],
            'profession': r[4] if r[4] else 'Student'
        }
        for r in cursor.fetchall()
    ]

    cursor.close(); mydb.close()

    room_dict = {
        'room_id':          room_data[0],
        'room_name':        room_data[1],
        'room_description': room_data[2],
        'admin_id':         room_data[3],
        'subject':          room_data[6] if len(room_data) > 6 else 'General',
        'room_notes':       room_data[7] if len(room_data) > 7 else '',
        'has_password':     bool(room_data[8]) if len(room_data) > 8 else False,
        'total_minutes':    room_data[10] if len(room_data) > 10 else 0,
    }

    return render_template('pages/room.html',
                           user=session, room=room_dict,
                           members=members, messages=messages,
                           is_admin=is_admin)


# ── API: Create Room ──────────────────────────────────────────

@classroom_bp.route('/api/create-room', methods=['POST'])
@login_required
def create_room():
    user_id     = session['user_id']
    room_name   = request.form.get('room_name', '').strip()
    description = request.form.get('room_description', '').strip()
    subject     = request.form.get('subject', 'General').strip()
    password    = request.form.get('room_password', '').strip() or None
    today       = date.today()

    if not room_name:
        return jsonify({'success': False, 'error': 'Room name is required'})

    mydb   = get_db_connection()
    cursor = mydb.cursor()

    cursor.execute("""
        INSERT INTO classroom
            (room_name, room_description, admin_id, created_date, total_duration, subject, room_notes, room_password, status, total_minutes)
        VALUES (%s, %s, %s, %s, '0h', %s, '', %s, 'active', 0)
    """, (room_name, description, user_id, today, subject, password))

    mydb.commit()
    room_id = cursor.lastrowid
    cursor.close()
    mydb.close()

    # Award +1 Stack for creating a room
    result = award_stack(user_id, 'room_created', 1)
    log_activity(user_id, 'room', f'Created room "{room_name}"')
    session['stacks'] = result.get('new_total', session.get('stacks', 0))

    return jsonify({
        'success':    True,
        'room_id':    room_id,
        'new_stacks': result.get('new_total', 0),
        'room_name':  room_name
    })


# ── API: Join Room ────────────────────────────────────────────

@classroom_bp.route('/api/join-room', methods=['POST'])
@login_required
def join_room_api():
    user_id  = session['user_id']
    room_id  = request.form.get('room_id')
    password = request.form.get('password', '').strip()
    today    = date.today()

    mydb   = get_db_connection()
    cursor = mydb.cursor()

    # Get room details
    cursor.execute(
        "SELECT admin_id, room_password, status FROM classroom WHERE room_id=%s",
        (room_id,)
    )
    room = cursor.fetchone()

    if not room:
        cursor.close(); mydb.close()
        return jsonify({'success': False, 'error': 'Room not found'})

    admin_id, room_password, room_status = room[0], room[1], room[2]

    # Admin of this room — just redirect, don't add as member
    if admin_id == user_id:
        cursor.close(); mydb.close()
        return jsonify({'success': True, 'message': 'You are the admin', 'room_id': room_id})

    # Closed room
    if room_status == 'closed':
        cursor.close(); mydb.close()
        return jsonify({'success': False, 'error': 'This room has been closed by the admin'})

    # Password check
    if room_password and room_password != password:
        cursor.close(); mydb.close()
        return jsonify({'success': False, 'error': 'Incorrect password'})

    # Already a member?
    cursor.execute(
        "SELECT member_id FROM room_members WHERE room_id=%s AND member_id=%s",
        (room_id, user_id)
    )
    already = cursor.fetchone()

    awarded_stack = False
    if not already:
        # First time join — add + award stack
        cursor.execute(
            "INSERT INTO room_members (member_id, room_id, join_date, join_time) VALUES (%s, %s, %s, %s)",
            (user_id, room_id, today, datetime.now())
        )
        mydb.commit()
        cursor.close(); mydb.close()

        result = award_stack(user_id, 'room_joined', 1)
        log_activity(user_id, 'room', f'Joined room #{room_id}')
        session['stacks'] = result.get('new_total', session.get('stacks', 0))
        awarded_stack = True
    else:
        cursor.close(); mydb.close()

    return jsonify({
        'success':       True,
        'message':       'Joined!' if not already else 'Already a member',
        'room_id':       room_id,
        'awarded_stack': awarded_stack
    })


# ── API: Close Room (Admin only — permanent) ──────────────────

@classroom_bp.route('/api/close-room', methods=['POST'])
@login_required
def close_room():
    user_id = session['user_id']
    room_id = request.form.get('room_id')

    mydb   = get_db_connection()
    cursor = mydb.cursor()

    cursor.execute("SELECT admin_id FROM classroom WHERE room_id=%s", (room_id,))
    row = cursor.fetchone()

    if not row or row[0] != user_id:
        cursor.close(); mydb.close()
        return jsonify({'success': False, 'error': 'Not authorized'})

    cursor.execute("UPDATE classroom SET status='closed' WHERE room_id=%s", (room_id,))
    mydb.commit()
    cursor.close(); mydb.close()

    log_activity(user_id, 'room', f'Closed room #{room_id}')
    return jsonify({'success': True})


# ── API: Leave Room (Member — removes from members list) ──────

@classroom_bp.route('/api/leave-room', methods=['POST'])
@login_required
def leave_room():
    user_id = session['user_id']
    room_id = request.form.get('room_id')

    mydb   = get_db_connection()
    cursor = mydb.cursor()

    cursor.execute(
        "DELETE FROM room_members WHERE room_id=%s AND member_id=%s",
        (room_id, user_id)
    )
    mydb.commit()
    cursor.close(); mydb.close()

    log_activity(user_id, 'room', f'Left room #{room_id}')
    return jsonify({'success': True})


# ── API: Update Session Time ──────────────────────────────────

@classroom_bp.route('/api/update-session-time', methods=['POST'])
@login_required
def update_session_time():
    """Called when user leaves a room — tracks hours spent."""
    room_id = request.form.get('room_id')
    minutes = int(request.form.get('minutes', 0))

    if minutes > 0 and minutes < 600:   # max 10h safety cap
        mydb   = get_db_connection()
        cursor = mydb.cursor()
        cursor.execute(
            "UPDATE classroom SET total_minutes = total_minutes + %s WHERE room_id=%s",
            (minutes, room_id)
        )
        mydb.commit()
        cursor.close(); mydb.close()

    return jsonify({'success': True})


# ── API: Get My Created Rooms ─────────────────────────────────

@classroom_bp.route('/api/get-my-rooms')
@login_required
def get_my_rooms():
    user_id = session['user_id']
    mydb    = get_db_connection()
    cursor  = mydb.cursor()

    cursor.execute("""
        SELECT room_id, room_name, room_description, created_date, subject,
               room_password, status, total_minutes
        FROM classroom
        WHERE admin_id=%s
        ORDER BY created_date DESC
    """, (user_id,))
    rows = cursor.fetchall()

    # Member count per room
    result = []
    for r in rows:
        cursor.execute(
            "SELECT COUNT(*) FROM room_members WHERE room_id=%s", (r[0],)
        )
        member_count = cursor.fetchone()[0]
        result.append({
            'room_id':      r[0],
            'room_name':    r[1],
            'description':  r[2],
            'created_date': str(r[3]),
            'subject':      r[4] or 'General',
            'has_password': bool(r[5]),
            'status':       r[6] or 'active',
            'total_minutes': r[7] or 0,
            'member_count': member_count
        })

    cursor.close(); mydb.close()
    return jsonify(result)


# ── API: Get Joined Rooms ─────────────────────────────────────

@classroom_bp.route('/api/get-joined-rooms')
@login_required
def get_joined_rooms():
    user_id = session['user_id']
    mydb    = get_db_connection()
    cursor  = mydb.cursor()

    cursor.execute("""
        SELECT c.room_id, c.room_name, c.room_description, rm.join_date,
               c.subject, c.status, u.profilename as admin_name
        FROM room_members rm
        JOIN classroom c ON c.room_id = rm.room_id
        JOIN users u ON u.user_id = c.admin_id
        WHERE rm.member_id=%s
        ORDER BY rm.join_date DESC
    """, (user_id,))
    rows = cursor.fetchall()
    cursor.close(); mydb.close()

    return jsonify([
        {
            'room_id':    r[0],
            'room_name':  r[1],
            'description': r[2],
            'join_date':  str(r[3]),
            'subject':    r[4] or 'General',
            'status':     r[5] or 'active',
            'admin_name': r[6]
        }
        for r in rows
    ])


# ── API: Get Classroom Stats ──────────────────────────────────

@classroom_bp.route('/api/get-classroom-stats')
@login_required
def get_classroom_stats():
    user_id = session['user_id']
    mydb    = get_db_connection()
    cursor  = mydb.cursor()

    cursor.execute("SELECT COUNT(*) FROM classroom WHERE admin_id=%s", (user_id,))
    created = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM room_members WHERE member_id=%s", (user_id,))
    joined = cursor.fetchone()[0]

    # Total hours: sum of total_minutes from rooms I created + rooms I joined
    cursor.execute(
        "SELECT COALESCE(SUM(c.total_minutes),0) FROM classroom c WHERE c.admin_id=%s",
        (user_id,)
    )
    mins_created = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COALESCE(SUM(c.total_minutes),0)
        FROM room_members rm
        JOIN classroom c ON c.room_id=rm.room_id
        WHERE rm.member_id=%s
    """, (user_id,))
    mins_joined = cursor.fetchone()[0]

    cursor.execute("SELECT stacks FROM users WHERE user_id=%s", (user_id,))
    stacks_row = cursor.fetchone()
    stacks = stacks_row[0] if stacks_row else 0

    cursor.close(); mydb.close()

    total_mins = (mins_created or 0) + (mins_joined or 0)
    hours      = round(total_mins / 60, 1)

    return jsonify({
        'rooms_created': created,
        'rooms_joined':  joined,
        'hours_spent':   hours,
        'stacks':        stacks
    })


# ── API: Delete Room ──────────────────────────────────────────

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
        return jsonify({'success': False, 'error': 'Not authorized'})

    cursor.execute("DELETE FROM room_members WHERE room_id=%s", (room_id,))
    cursor.execute("DELETE FROM classroom_messages WHERE room_id=%s", (room_id,))
    cursor.execute("DELETE FROM classroom WHERE room_id=%s", (room_id,))
    mydb.commit()
    cursor.close(); mydb.close()

    return jsonify({'success': True})


# ── API: Remove Room Member ───────────────────────────────────

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
        return jsonify({'success': False, 'error': 'Not authorized'})

    cursor.execute(
        "DELETE FROM room_members WHERE room_id=%s AND member_id=%s",
        (room_id, member_id)
    )
    mydb.commit()
    cursor.close(); mydb.close()
    return jsonify({'success': True})


# ── API: Collaborative Notes ──────────────────────────────────

@classroom_bp.route('/api/save-room-notes', methods=['POST'])
@login_required
def save_room_notes():
    user_id = session['user_id']
    room_id = request.form.get('room_id')
    notes   = request.form.get('notes', '')

    mydb   = get_db_connection()
    cursor = mydb.cursor()

    cursor.execute(
        "SELECT admin_id FROM classroom WHERE room_id=%s", (room_id,)
    )
    room = cursor.fetchone()
    if not room:
        cursor.close(); mydb.close()
        return jsonify({'success': False, 'error': 'Room not found'})

    cursor.execute(
        "UPDATE classroom SET room_notes=%s WHERE room_id=%s",
        (notes, room_id)
    )
    mydb.commit()
    cursor.close(); mydb.close()

    result = award_stack(user_id, 'room_notes_saved', 1)
    log_activity(user_id, 'notes', f'Saved collaborative notes in room #{room_id}')
    session['stacks'] = result.get('new_total', session.get('stacks', 0))

    return jsonify({
        'success':    True,
        'message':    'Notes saved! +1 Stack 🔥',
        'new_stacks': result.get('new_total', 0)
    })


@classroom_bp.route('/api/get-room-notes/<int:room_id>')
@login_required
def get_room_notes(room_id):
    mydb   = get_db_connection()
    cursor = mydb.cursor()
    cursor.execute("SELECT room_notes FROM classroom WHERE room_id=%s", (room_id,))
    row = cursor.fetchone()
    cursor.close(); mydb.close()
    return jsonify({'notes': row[0] if row and row[0] else ''})
