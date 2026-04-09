# ============================================================
# routes/profile.py — Profile + Settings + Avatar + Delete
# Rule 4: All profile features fully functional
# ============================================================

import os
from flask import Blueprint, render_template, request, session, redirect, url_for, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from db import get_db_connection
from functools import wraps
from helpers.stacks import log_activity

profile_bp = Blueprint('profile', __name__)


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated


# ── Profile Page ─────────────────────────────────────────────

@profile_bp.route('/profile')
@login_required
def profile():
    user_id = session['user_id']
    mydb    = get_db_connection()
    cursor  = mydb.cursor()

    cursor.execute("SELECT * FROM users WHERE user_id=%s", (user_id,))
    user_data = cursor.fetchone()

    if not user_data:
        cursor.close(); mydb.close()
        return redirect(url_for('auth.logout'))

    # Followers / Following counts
    cursor.execute("SELECT COUNT(*) FROM follows WHERE following_id=%s", (user_id,))
    followers_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM follows WHERE follower_id=%s", (user_id,))
    following_count = cursor.fetchone()[0]

    # Recent activity (last 10)
    cursor.execute("""
        SELECT action_type, action_desc, created_at
        FROM activity_log WHERE user_id=%s
        ORDER BY created_at DESC LIMIT 10
    """, (user_id,))
    recent_activity = [
        {'type': r[0], 'desc': r[1],
         'time': r[2].strftime("%b %d, %I:%M %p") if r[2] else ''}
        for r in cursor.fetchall()
    ]

    cursor.close(); mydb.close()

    # Map user_data columns to a dict
    # Columns: 0:user_id, 1:profile_pic, 2:bg_pic, 3:profilename, 4:username,
    #   5:whatsapp, 6:email, 7:password, 8:bio, 9:created_date,
    #   10:profession, 11:stacks, 12:streak, 13:last_login_date,
    #   14:email_notif, 15:whatsapp_notif, 16:notif_channel,
    #   17:privacy, 18:show_activity, 19:avatar_id
    def safe(idx, default=''):
        return user_data[idx] if len(user_data) > idx and user_data[idx] is not None else default

    user_dict = {
        'user_id':        safe(0),
        'profile_pic':    safe(1),
        'bg_pic':         safe(2),
        'profilename':    safe(3),
        'username':       safe(4),
        'whatsapp':       safe(5),
        'email':          safe(6),
        'bio':            safe(8),
        'created_date':   str(safe(9, '')),
        'profession':     safe(10, 'Student'),
        'stacks':         int(safe(11, 0)),
        'streak':         int(safe(12, 0)),
        'email_notif':    bool(safe(14, 1)),
        'whatsapp_notif': bool(safe(15, 0)),
        'notif_channel':  safe(16, 'email'),
        'privacy':        safe(17, 'public'),
        'show_activity':  bool(safe(18, 1)),
        'avatar_id':      int(safe(19, 1)),
        'followers':      followers_count,
        'following':      following_count,
    }

    return render_template('pages/profile.html',
                           user=session,
                           profile=user_dict,
                           recent_activity=recent_activity)


# ── Update Profile ───────────────────────────────────────────

@profile_bp.route('/api/update-profile', methods=['POST'])
@login_required
def update_profile():
    user_id     = session['user_id']
    profilename = request.form.get('profilename', '').strip()
    username    = request.form.get('username', '').strip().lower()
    whatsapp    = request.form.get('whatsapp', '').strip()
    bio         = request.form.get('bio', '').strip()
    profession  = request.form.get('profession', 'Student')

    mydb   = get_db_connection()
    cursor = mydb.cursor()

    cursor.execute("""
        UPDATE users
        SET profilename=%s, username=%s, whatsapp=%s, bio=%s, profession=%s
        WHERE user_id=%s
    """, (profilename, username, whatsapp, bio, profession, user_id))

    # Handle profile picture upload
    p1 = request.files.get('profilePicInput')
    if p1 and p1.filename:
        ext        = os.path.splitext(p1.filename)[1]
        profile_pic = f"user{ext}"
        upload_dir  = os.path.join('static', 'images', 'users', str(user_id))
        os.makedirs(upload_dir, exist_ok=True)
        p1.save(os.path.join(upload_dir, profile_pic))
        cursor.execute("UPDATE users SET profile_pic=%s WHERE user_id=%s", (profile_pic, user_id))
        session['profile_pic'] = profile_pic

    # Handle background picture upload
    b1 = request.files.get('coverPicInput')
    if b1 and b1.filename:
        ext    = os.path.splitext(b1.filename)[1]
        bg_pic = f"cover{ext}"
        bg_dir = os.path.join('static', 'images', 'background', str(user_id))
        os.makedirs(bg_dir, exist_ok=True)
        b1.save(os.path.join(bg_dir, bg_pic))
        cursor.execute("UPDATE users SET background_pic=%s WHERE user_id=%s", (bg_pic, user_id))
        session['bg_pic'] = bg_pic

    mydb.commit()

    session['profilename'] = profilename
    session['username']    = username
    session['profession']  = profession

    cursor.close(); mydb.close()

    log_activity(user_id, 'profile', 'Updated profile information')
    return jsonify({"success": True, "message": "Profile updated!"})


# ── Avatar Selection ─────────────────────────────────────────

@profile_bp.route('/api/set-avatar', methods=['POST'])
@login_required
def set_avatar():
    """Set avatar_id (1-12) for the user."""
    user_id   = session['user_id']
    avatar_id = request.form.get('avatar_id', 1, type=int)

    if not (1 <= avatar_id <= 12):
        return jsonify({"success": False, "error": "Invalid avatar"})

    mydb   = get_db_connection()
    cursor = mydb.cursor()
    cursor.execute("UPDATE users SET avatar_id=%s WHERE user_id=%s", (avatar_id, user_id))
    mydb.commit()
    cursor.close(); mydb.close()

    return jsonify({"success": True, "avatar_id": avatar_id})


# ── Save Settings ────────────────────────────────────────────

@profile_bp.route('/api/save-settings', methods=['POST'])
@login_required
def save_settings():
    """Save all notification and privacy settings."""
    user_id        = session['user_id']
    email_notif    = 1 if request.form.get('email_notif') == 'true' else 0
    whatsapp_notif = 1 if request.form.get('whatsapp_notif') == 'true' else 0
    notif_channel  = request.form.get('notif_channel', 'email')
    privacy        = request.form.get('privacy', 'public')
    show_activity  = 1 if request.form.get('show_activity') == 'true' else 0

    mydb   = get_db_connection()
    cursor = mydb.cursor()

    cursor.execute("""
        UPDATE users
        SET email_notif=%s, whatsapp_notif=%s, notif_channel=%s,
            privacy=%s, show_activity=%s
        WHERE user_id=%s
    """, (email_notif, whatsapp_notif, notif_channel, privacy, show_activity, user_id))

    mydb.commit()
    cursor.close(); mydb.close()

    return jsonify({"success": True, "message": "Settings saved!"})


# ── Change Password ──────────────────────────────────────────

@profile_bp.route('/api/change-password', methods=['POST'])
@login_required
def change_password():
    user_id      = session['user_id']
    current_pwd  = request.form.get('current_password', '')
    new_pwd      = request.form.get('new_password', '')
    confirm_pwd  = request.form.get('confirm_password', '')

    if new_pwd != confirm_pwd:
        return jsonify({"success": False, "error": "Passwords do not match"})

    if len(new_pwd) < 6:
        return jsonify({"success": False, "error": "Password must be at least 6 characters"})

    mydb   = get_db_connection()
    cursor = mydb.cursor()

    cursor.execute("SELECT password FROM users WHERE user_id=%s", (user_id,))
    row = cursor.fetchone()
    if not row:
        cursor.close(); mydb.close()
        return jsonify({"success": False, "error": "User not found"})

    stored = row[0]
    # Verify current password (supports both plain and hashed)
    if stored.startswith('pbkdf2:') or stored.startswith('scrypt:'):
        valid = check_password_hash(stored, current_pwd)
    else:
        valid = (stored == current_pwd)

    if not valid:
        cursor.close(); mydb.close()
        return jsonify({"success": False, "error": "Current password is incorrect"})

    hashed = generate_password_hash(new_pwd)
    cursor.execute("UPDATE users SET password=%s WHERE user_id=%s", (hashed, user_id))
    mydb.commit()
    cursor.close(); mydb.close()

    log_activity(user_id, 'security', 'Changed password')
    return jsonify({"success": True, "message": "Password changed successfully!"})


# ── Delete Account ───────────────────────────────────────────

@profile_bp.route('/api/delete-account', methods=['POST'])
@login_required
def delete_account():
    """Permanently delete user account and all associated data."""
    user_id      = session['user_id']
    confirm_text = request.form.get('confirm_text', '')

    if confirm_text.strip().upper() != 'DELETE':
        return jsonify({"success": False, "error": "Type DELETE to confirm"})

    mydb   = get_db_connection()
    cursor = mydb.cursor()

    try:
        # Delete all user data in correct order
        cursor.execute("DELETE FROM task_completions WHERE user_id=%s", (user_id,))
    except Exception:
        pass  # table may not exist

    cursor.execute("DELETE FROM tasks WHERE user_id=%s", (user_id,))
    cursor.execute("DELETE FROM focus WHERE user_id=%s", (user_id,))
    cursor.execute("DELETE FROM notes WHERE user_id=%s", (user_id,))
    cursor.execute("DELETE FROM uploaded_files WHERE user_id=%s", (user_id,))
    cursor.execute("DELETE FROM follows WHERE follower_id=%s OR following_id=%s", (user_id, user_id))
    cursor.execute("DELETE FROM post_likes WHERE user_id=%s", (user_id,))
    cursor.execute("DELETE FROM post_comments WHERE user_id=%s", (user_id,))
    cursor.execute("DELETE FROM posts WHERE user_id=%s", (user_id,))
    cursor.execute("DELETE FROM classroom_messages WHERE user_id=%s", (user_id,))
    cursor.execute("DELETE FROM community_messages WHERE user_id=%s", (user_id,))
    cursor.execute("DELETE FROM room_members WHERE member_id=%s", (user_id,))
    cursor.execute("DELETE FROM group_members WHERE member_id=%s", (user_id,))
    cursor.execute("DELETE FROM stack_history WHERE user_id=%s", (user_id,))
    cursor.execute("DELETE FROM activity_log WHERE user_id=%s", (user_id,))
    cursor.execute("DELETE FROM users WHERE user_id=%s", (user_id,))

    mydb.commit()
    cursor.close(); mydb.close()

    session.clear()
    return jsonify({"success": True, "message": "Account deleted."})


# ── Get Profile (JSON for sidebar) ──────────────────────────

@profile_bp.route('/api/get-profile')
@login_required
def get_profile():
    user_id = session['user_id']
    mydb    = get_db_connection()
    cursor  = mydb.cursor()

    cursor.execute("""
        SELECT profilename, username, email, profile_pic,
               profession, stacks, streak
        FROM users WHERE user_id=%s
    """, (user_id,))
    row = cursor.fetchone()

    # Followers
    cursor.execute("SELECT COUNT(*) FROM follows WHERE following_id=%s", (user_id,))
    followers = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM follows WHERE follower_id=%s", (user_id,))
    following = cursor.fetchone()[0]

    cursor.close(); mydb.close()

    if row:
        return jsonify({
            'profilename': row[0],
            'username':    row[1],
            'email':       row[2],
            'profile_pic': row[3],
            'profession':  row[4] or 'Student',
            'stacks':      int(row[5]) if row[5] else 0,
            'streak':      int(row[6]) if row[6] else 0,
            'followers':   followers,
            'following':   following
        })
    return jsonify({})


# ── Follow / Unfollow ────────────────────────────────────────

@profile_bp.route('/api/follow-user', methods=['POST'])
@login_required
def follow_user():
    follower_id  = session['user_id']
    following_id = request.form.get('user_id', type=int)

    if follower_id == following_id:
        return jsonify({"success": False, "error": "Cannot follow yourself"})

    mydb   = get_db_connection()
    cursor = mydb.cursor()

    cursor.execute(
        "SELECT follow_id FROM follows WHERE follower_id=%s AND following_id=%s",
        (follower_id, following_id)
    )
    existing = cursor.fetchone()

    if existing:
        cursor.execute(
            "DELETE FROM follows WHERE follower_id=%s AND following_id=%s",
            (follower_id, following_id)
        )
        action = 'unfollowed'
    else:
        cursor.execute(
            "INSERT IGNORE INTO follows (follower_id, following_id) VALUES (%s, %s)",
            (follower_id, following_id)
        )
        action = 'followed'

    mydb.commit()

    # Get updated counts
    cursor.execute("SELECT COUNT(*) FROM follows WHERE following_id=%s", (following_id,))
    followers = cursor.fetchone()[0]

    cursor.close(); mydb.close()

    return jsonify({"success": True, "action": action, "followers": followers})


# ── Get Followers / Following ────────────────────────────────

@profile_bp.route('/api/get-follow-counts')
@login_required
def get_follow_counts():
    user_id = session['user_id']
    mydb    = get_db_connection()
    cursor  = mydb.cursor()

    cursor.execute("SELECT COUNT(*) FROM follows WHERE following_id=%s", (user_id,))
    followers = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM follows WHERE follower_id=%s", (user_id,))
    following = cursor.fetchone()[0]

    cursor.close(); mydb.close()

    return jsonify({"followers": followers, "following": following})
