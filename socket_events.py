# ============================================================
# socket_events.py — Flask-SocketIO Event Handlers
# Updated: Refactored to avoid circular imports
# ============================================================

from flask import session, request
from flask_socketio import emit, join_room, leave_room
from db import get_db_connection
from datetime import datetime
from helpers.notifications import send_email, notify_user

def init_socket_events(socketio):

    @socketio.on_error_default
    def default_error_handler(e):
        print(f"[Socket Error] {e}")

    @socketio.on('*')
    def catch_all(event, data):
        # Useful for debugging incoming events
        print(f"[Socket Event] {event}: {data}")

    # ==============================================================
    # CLASSROOM — Room-based Text Chat
    # ==============================================================

    @socketio.on('join_classroom_room')
    def handle_join_classroom_room(data):
        room_id    = str(data.get('room_id'))
        user_id    = session.get('user_id')
        username   = data.get('username') or session.get('profilename', 'User')
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
        room_id  = str(data.get('room_id'))
        username = session.get('profilename', 'User')
        user_id  = session.get('user_id')

        leave_room(f"classroom_{room_id}")

        emit('classroom_user_left', {
            'user_id':  user_id,
            'username': username,
            'message':  f"{username} left the room"
        }, to=f"classroom_{room_id}")


    @socketio.on('close_classroom_room')
    def handle_close_classroom_room(data):
        """Admin closes room — broadcast room_closed to all members so they get redirected."""
        room_id  = str(data.get('room_id'))
        username = session.get('profilename', 'Admin')

        emit('room_closed', {
            'message': f"Room closed by {username}"
        }, to=f"classroom_{room_id}")

        leave_room(f"classroom_{room_id}")


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
            print(f"[Socket] Classroom DB error: {e}")

        emit('classroom_new_message', {
            'user_id':    user_id,
            'username':   username,
            'profession': profession,
            'message':    message,
            'time':       datetime.now().strftime("%I:%M %p")
        }, to=f"classroom_{room_id}")


    # ==============================================================
    # CLASSROOM — Collaborative Notes
    # ==============================================================

    @socketio.on('room_notes_update')
    def handle_room_notes_update(data):
        room_id       = str(data.get('room_id'))
        notes_content = data.get('notes_content', '')
        username      = session.get('profilename', 'User')

        emit('room_notes_changed', {
            'notes_content': notes_content,
            'by':            username
        }, to=f"classroom_{room_id}", include_self=False)


    @socketio.on('save_room_notes_socket')
    def handle_save_room_notes(data):
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
            cursor.execute("UPDATE users SET stacks = stacks + 1 WHERE user_id=%s", (user_id,))
            cursor.execute("INSERT INTO stack_history (user_id, reason, stacks_given) VALUES (%s, %s, 1)", (user_id, 'room_notes_saved'))
            mydb.commit()
            cursor.close()
            mydb.close()

            emit('room_notes_saved', {
                'success': True,
                'by':      username,
                'message': f'Notes saved by {username} (+1 Stack!)'
            }, to=f"classroom_{room_id}")

        except Exception as e:
            print(f"[Socket] Notes save error: {e}")


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
        file_url   = data.get('file_url')
        file_name  = data.get('file_name')
        file_type  = data.get('file_type')
        
        room_key   = f"community_{group_id}_{subject}"
        user_id    = session.get('user_id')
        username   = session.get('profilename', 'User')
        profession = session.get('profession', 'Student')

        print(f"[Socket DEBUG] Received community message from user {user_id} in group {group_id}")

        if not message and not file_url:
            return

        # If session user_id is missing, we might have a session issue.
        # But for now, we assume it's there.
        if not user_id:
            print("[Socket ERROR] Missing user_id in session for community_send_message")
            return

        try:
            mydb   = get_db_connection()
            cursor = mydb.cursor()
            cursor.execute(
                "INSERT INTO community_messages (group_id, user_id, subject, message, file_url, file_name, file_type) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                (group_id, user_id, subject, message, file_url, file_name, file_type)
            )
            mydb.commit()
            cursor.close()
            mydb.close()
        except Exception as e:
            print(f"[Socket] Community DB Error: {e}")
            emit('community_error', {'error': 'Failed to save message'})
            return

        emit('community_new_message', {
            'user_id':    user_id,
            'username':   username,
            'profession': profession,
            'subject':    subject,
            'message':    message,
            'file_url':   file_url,
            'file_name':  file_name,
            'file_type':  file_type,
            'time':       datetime.now().strftime("%I:%M %p")
        }, to=room_key)

        # Notify offline members (Simple version: everyone in group except sender)
        try:
            mydb2   = get_db_connection()
            cursor2 = mydb2.cursor(dictionary=True)
            cursor2.execute("""
                SELECT u.email, u.profilename, u.notif_channel
                FROM group_members gm
                JOIN users u ON u.user_id = gm.member_id
                WHERE gm.group_id = %s AND u.user_id != %s
            """, (group_id, user_id))
            members = cursor2.fetchall()
            
            notif_body = f"New message in {subject} group from {username}:\n\n\"{message[:100]}\""
            for member in members:
                # We use notify_user which respects user's channel preference
                notify_user(member, f"Group Alert: {subject}", notif_body)
            
            cursor2.close()
            mydb2.close()
        except Exception as e:
            print(f"[Socket Notif] Error notifying members: {e}")


    # ==============================================================
    # PROFILE — Real-time Follow Count Updates
    # ==============================================================

    @socketio.on('follow_user_socket')
    def handle_follow_socket(data):
        target_user_id = data.get('target_user_id')
        follower_name  = session.get('profilename', 'Someone')

        try:
            mydb   = get_db_connection()
            cursor = mydb.cursor()
            cursor.execute("SELECT COUNT(*) FROM follows WHERE following_id=%s", (target_user_id,))
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