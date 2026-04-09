# ============================================================
# socket_events.py — Flask-SocketIO Event Handlers
# Updated: Room notes collaboration + follow notifications
# ============================================================

from flask import session, request
from flask_socketio import emit, join_room, leave_room
from app import socketio
from db import get_db_connection
from datetime import datetime


# ==============================================================
# CLASSROOM — Room-based Text Chat
# ==============================================================

@socketio.on('join_classroom_room')
def handle_join_classroom_room(data):
    room_id  = str(data.get('room_id'))
    user_id  = session.get('user_id')
    username = session.get('profilename', 'User')
    profession = session.get('profession', 'Student')

    join_room(f"classroom_{room_id}")

    emit('classroom_user_joined', {
        'user_id':    user_id,
        'username':   username,
        'profession': profession,
        'message':    f"{username} joined the room"
    }, to=f"classroom_{room_id}")


@socketio.on('leave_classroom_room')
def handle_leave_classroom_room(data):
    room_id    = str(data.get('room_id'))
    username   = session.get('profilename', 'User')

    leave_room(f"classroom_{room_id}")

    emit('classroom_user_left', {
        'username': username,
        'message':  f"{username} left the room"
    }, to=f"classroom_{room_id}")


@socketio.on('classroom_send_message')
def handle_classroom_message(data):
    room_id    = str(data.get('room_id'))
    message    = data.get('message', '').strip()
    user_id    = session.get('user_id')
    username   = session.get('profilename', 'User')
    profession = session.get('profession', 'Student')

    if not message:
        return

    try:
        mydb   = get_db_connection()
        cursor = mydb.cursor()
        cursor.execute(
            "INSERT INTO classroom_messages (room_id, user_id, message) VALUES (%s, %s, %s)",
            (room_id, user_id, message)
        )
        mydb.commit()
        cursor.close()
        mydb.close()
    except Exception as e:
        print(f"[Socket] DB error: {e}")

    emit('classroom_new_message', {
        'user_id':    user_id,
        'username':   username,
        'profession': profession,
        'message':    message,
        'time':       datetime.now().strftime("%I:%M %p")
    }, to=f"classroom_{room_id}")


# ==============================================================
# CLASSROOM — Collaborative Notes via SocketIO
# ==============================================================

@socketio.on('room_notes_update')
def handle_room_notes_update(data):
    """
    Broadcast note changes to all room members in real-time.
    data = { room_id, notes_content }
    """
    room_id       = str(data.get('room_id'))
    notes_content = data.get('notes_content', '')
    username      = session.get('profilename', 'User')

    # Broadcast to all others in the room (not self)
    emit('room_notes_changed', {
        'notes_content': notes_content,
        'by':            username
    }, to=f"classroom_{room_id}", include_self=False)


@socketio.on('save_room_notes_socket')
def handle_save_room_notes(data):
    """
    Save collaborative notes to DB via socket.
    Triggered when user clicks 'Save Notes' or leaves the room.
    data = { room_id, notes_content }
    """
    room_id       = data.get('room_id')
    notes_content = data.get('notes_content', '')
    user_id       = session.get('user_id')
    username      = session.get('profilename', 'User')

    try:
        mydb   = get_db_connection()
        cursor = mydb.cursor()
        cursor.execute(
            "UPDATE classroom SET room_notes=%s WHERE room_id=%s",
            (notes_content, room_id)
        )

        # Award +1 Stack
        cursor.execute(
            "UPDATE users SET stacks = stacks + 1 WHERE user_id=%s",
            (user_id,)
        )
        cursor.execute(
            "INSERT INTO stack_history (user_id, reason, stacks_given) VALUES (%s, %s, 1)",
            (user_id, 'room_notes_saved')
        )
        cursor.execute(
            "INSERT INTO activity_log (user_id, action_type, action_desc) VALUES (%s, %s, %s)",
            (user_id, 'notes', f'Saved collaborative notes in room #{room_id}')
        )

        cursor.execute("SELECT stacks FROM users WHERE user_id=%s", (user_id,))
        row        = cursor.fetchone()
        new_stacks = row[0] if row else 0

        mydb.commit()
        cursor.close()
        mydb.close()

        emit('room_notes_saved', {
            'success':    True,
            'by':         username,
            'new_stacks': new_stacks,
            'message':    f'Notes saved by {username} (+1 Stack!)'
        }, to=f"classroom_{room_id}")

    except Exception as e:
        print(f"[Socket] Notes save error: {e}")
        emit('room_notes_saved', {'success': False, 'error': str(e)})


# ==============================================================
# CLASSROOM — WebRTC Video Chat Signaling
# ==============================================================

@socketio.on('webrtc_offer')
def handle_webrtc_offer(data):
    emit('webrtc_offer', {
        'from_sid': request.sid,
        'offer':    data.get('offer')
    }, to=data.get('target_sid'))


@socketio.on('webrtc_answer')
def handle_webrtc_answer(data):
    emit('webrtc_answer', {
        'from_sid': request.sid,
        'answer':   data.get('answer')
    }, to=data.get('target_sid'))


@socketio.on('webrtc_ice_candidate')
def handle_ice_candidate(data):
    emit('webrtc_ice_candidate', {
        'from_sid':  request.sid,
        'candidate': data.get('candidate')
    }, to=data.get('target_sid'))


@socketio.on('webrtc_user_ready')
def handle_user_ready(data):
    room_id    = str(data.get('room_id'))
    username   = session.get('profilename', 'User')
    profession = session.get('profession', 'Student')

    emit('webrtc_new_peer', {
        'sid':        request.sid,
        'username':   username,
        'profession': profession
    }, to=f"classroom_{room_id}", include_self=False)


# ==============================================================
# COMMUNITY — Per-Subject Chat Rooms
# ==============================================================

@socketio.on('join_community_room')
def handle_join_community_room(data):
    subject    = data.get('subject', 'general')
    group_id   = str(data.get('group_id'))
    room_key   = f"community_{group_id}_{subject}"
    username   = session.get('profilename', 'User')
    profession = session.get('profession', 'Student')

    join_room(room_key)

    emit('community_user_joined', {
        'username':   username,
        'profession': profession,
        'message':    f"{username} joined #{subject}"
    }, to=room_key)


@socketio.on('leave_community_room')
def handle_leave_community_room(data):
    subject  = data.get('subject', 'general')
    group_id = str(data.get('group_id'))
    room_key = f"community_{group_id}_{subject}"
    username = session.get('profilename', 'User')

    leave_room(room_key)

    emit('community_user_left', {
        'username': username,
        'message':  f"{username} left #{subject}"
    }, to=room_key)


@socketio.on('community_send_message')
def handle_community_message(data):
    subject    = data.get('subject', 'general')
    group_id   = str(data.get('group_id'))
    message    = data.get('message', '').strip()
    room_key   = f"community_{group_id}_{subject}"
    user_id    = session.get('user_id')
    username   = session.get('profilename', 'User')
    profession = session.get('profession', 'Student')

    if not message:
        return

    try:
        mydb   = get_db_connection()
        cursor = mydb.cursor()
        cursor.execute(
            "INSERT INTO community_messages (group_id, user_id, subject, message) VALUES (%s, %s, %s, %s)",
            (group_id, user_id, subject, message)
        )
        mydb.commit()
        cursor.close()
        mydb.close()
    except Exception as e:
        print(f"[Socket] Community DB error: {e}")

    emit('community_new_message', {
        'user_id':    user_id,
        'username':   username,
        'profession': profession,
        'subject':    subject,
        'message':    message,
        'time':       datetime.now().strftime("%I:%M %p")
    }, to=room_key)


# ==============================================================
# PROFILE — Real-time Follow Count Updates
# ==============================================================

@socketio.on('follow_user_socket')
def handle_follow_socket(data):
    """Broadcast updated follower count to the target user's session."""
    target_user_id = data.get('target_user_id')
    follower_name  = session.get('profilename', 'Someone')

    try:
        mydb   = get_db_connection()
        cursor = mydb.cursor()
        cursor.execute(
            "SELECT COUNT(*) FROM follows WHERE following_id=%s",
            (target_user_id,)
        )
        followers = cursor.fetchone()[0]
        cursor.close()
        mydb.close()

        emit('follower_count_updated', {
            'user_id':       target_user_id,
            'followers':     followers,
            'follower_name': follower_name
        }, broadcast=True)

    except Exception as e:
        print(f"[Socket] Follow update error: {e}")
