# ============================================================
# socket_events.py — Flask-SocketIO Event Handlers
# Classroom room chat + Community subject chat yahan handle hota hai
# WebRTC signaling bhi yahan hota hai
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
    """
    User ek classroom room join karta hai.
    data = { room_id: 5 }
    """
    room_id = str(data.get('room_id'))
    user_id = session.get('user_id')
    username = session.get('profilename', 'User')

    join_room(f"classroom_{room_id}")

    # Sabko batao ki naya user aaya
    emit('classroom_user_joined', {
        'user_id': user_id,
        'username': username,
        'message': f"{username} joined the room"
    }, to=f"classroom_{room_id}")


@socketio.on('leave_classroom_room')
def handle_leave_classroom_room(data):
    """User room chhod raha hai."""
    room_id = str(data.get('room_id'))
    username = session.get('profilename', 'User')

    leave_room(f"classroom_{room_id}")

    emit('classroom_user_left', {
        'username': username,
        'message': f"{username} left the room"
    }, to=f"classroom_{room_id}")


@socketio.on('classroom_send_message')
def handle_classroom_message(data):
    """
    Text message bheja — sirf usi room ke logon ko dikhao.
    data = { room_id: 5, message: "Hello!" }
    """
    room_id = str(data.get('room_id'))
    message  = data.get('message', '').strip()
    user_id  = session.get('user_id')
    username = session.get('profilename', 'User')

    if not message:
        return

    # DB mein save karo
    try:
        mydb = get_db_connection()
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

    # Usi room ke sabko bhejo
    emit('classroom_new_message', {
        'user_id': user_id,
        'username': username,
        'message': message,
        'time': datetime.now().strftime("%I:%M %p")
    }, to=f"classroom_{room_id}")


# ==============================================================
# CLASSROOM — WebRTC Video Chat Signaling
# Mesh approach: har peer doosre se directly connect karta hai
# ==============================================================

@socketio.on('webrtc_offer')
def handle_webrtc_offer(data):
    """
    Peer A ek offer bhejta hai Peer B ko.
    data = { room_id, target_sid, offer }
    target_sid = jis user ko offer bhejna hai uska socket ID
    """
    emit('webrtc_offer', {
        'from_sid': request.sid,
        'offer': data.get('offer')
    }, to=data.get('target_sid'))


@socketio.on('webrtc_answer')
def handle_webrtc_answer(data):
    """
    Peer B answer bhejta hai Peer A ko.
    data = { target_sid, answer }
    """
    emit('webrtc_answer', {
        'from_sid': request.sid,
        'answer': data.get('answer')
    }, to=data.get('target_sid'))


@socketio.on('webrtc_ice_candidate')
def handle_ice_candidate(data):
    """
    ICE candidate exchange — yeh WebRTC connection ke liye zaroori hai.
    data = { target_sid, candidate }
    """
    emit('webrtc_ice_candidate', {
        'from_sid': request.sid,
        'candidate': data.get('candidate')
    }, to=data.get('target_sid'))


@socketio.on('webrtc_user_ready')
def handle_user_ready(data):
    """
    Jab user video ke liye ready ho, sabko apna socket ID batao
    taaki dusre users usse offer bhej sakein.
    data = { room_id }
    """
    room_id = str(data.get('room_id'))
    username = session.get('profilename', 'User')

    # Room ke sabko batao ki naya video user aaya
    emit('webrtc_new_peer', {
        'sid': request.sid,
        'username': username
    }, to=f"classroom_{room_id}", include_self=False)


# ==============================================================
# COMMUNITY — Per-Subject Chat Rooms
# ==============================================================

@socketio.on('join_community_room')
def handle_join_community_room(data):
    """
    User ek subject chat room join karta hai.
    data = { subject: "physics", group_id: 3 }
    """
    subject  = data.get('subject', 'general')
    group_id = str(data.get('group_id'))
    room_key = f"community_{group_id}_{subject}"

    user_id  = session.get('user_id')
    username = session.get('profilename', 'User')

    join_room(room_key)

    emit('community_user_joined', {
        'username': username,
        'message': f"{username} joined #{subject}"
    }, to=room_key)


@socketio.on('leave_community_room')
def handle_leave_community_room(data):
    """User community chat chhod raha hai."""
    subject  = data.get('subject', 'general')
    group_id = str(data.get('group_id'))
    room_key = f"community_{group_id}_{subject}"
    username = session.get('profilename', 'User')

    leave_room(room_key)

    emit('community_user_left', {
        'username': username,
        'message': f"{username} left #{subject}"
    }, to=room_key)


@socketio.on('community_send_message')
def handle_community_message(data):
    """
    Community chat message bhejo.
    data = { group_id, subject, message }
    Sirf us group ke members jo us subject room mein hain unhe dikhega.
    """
    subject  = data.get('subject', 'general')
    group_id = str(data.get('group_id'))
    message  = data.get('message', '').strip()
    room_key = f"community_{group_id}_{subject}"

    user_id  = session.get('user_id')
    username = session.get('profilename', 'User')

    if not message:
        return

    # DB mein save karo
    try:
        mydb = get_db_connection()
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
        'user_id': user_id,
        'username': username,
        'subject': subject,
        'message': message,
        'time': datetime.now().strftime("%I:%M %p")
    }, to=room_key)
