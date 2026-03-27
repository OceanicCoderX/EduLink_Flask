# ============================================================
# routes/profile.py — Profile Page + Edit API
# ============================================================

import os
from flask import Blueprint, render_template, request, session, redirect, url_for, jsonify
from db import get_db_connection
from functools import wraps

profile_bp = Blueprint('profile', __name__)


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated


@profile_bp.route('/profile')
@login_required
def profile():
    """Profile page — DB se user data fetch karo."""
    user_id = session['user_id']
    mydb    = get_db_connection()
    cursor  = mydb.cursor()

    cursor.execute("SELECT * FROM users WHERE user_id=%s", (user_id,))
    user_data = cursor.fetchone()

    # Focus stats
    cursor.execute(
        "SELECT COALESCE(SUM(stacks_earned),0), COALESCE(SUM(sessions_count),0) FROM focus WHERE user_id=%s",
        (user_id,)
    )
    stats = cursor.fetchone()

    cursor.close()
    mydb.close()

    if not user_data:
        return redirect(url_for('auth.logout'))

    user_dict = {
        'user_id':     user_data[0],
        'profile_pic': user_data[1],
        'bg_pic':      user_data[2],
        'profilename': user_data[3],
        'username':    user_data[4],
        'whatsapp':    user_data[5],
        'email':       user_data[6],
        'bio':         user_data[8],
        'created_date': str(user_data[9]),
        'total_stacks':  stats[0],
        'total_sessions': stats[1]
    }

    return render_template('pages/profile.html', user=session, profile=user_dict)


@profile_bp.route('/api/update-profile', methods=['POST'])
@login_required
def update_profile():
    """Profile info update karo."""
    user_id     = session['user_id']
    profilename = request.form.get('profilename')
    username    = request.form.get('username')
    whatsapp    = request.form.get('whatsapp')
    bio         = request.form.get('bio', '')

    mydb   = get_db_connection()
    cursor = mydb.cursor()

    cursor.execute("""
        UPDATE users SET profilename=%s, username=%s, whatsapp=%s, bio=%s
        WHERE user_id=%s
    """, (profilename, username, whatsapp, bio, user_id))

    # Handle profile picture upload
    p1 = request.files.get('profilePicInput')
    if p1 and p1.filename:
        ext = os.path.splitext(p1.filename)[1]
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

    # Session update karo
    session['profilename'] = profilename
    session['username']    = username

    cursor.close()
    mydb.close()

    return jsonify({"success": True, "message": "Profile updated!"})


@profile_bp.route('/api/get-profile')
@login_required
def get_profile():
    """Profile data JSON mein return karo (sidebar ke liye)."""
    user_id = session['user_id']
    mydb    = get_db_connection()
    cursor  = mydb.cursor()

    cursor.execute("SELECT profilename, username, email, profile_pic FROM users WHERE user_id=%s", (user_id,))
    row = cursor.fetchone()
    cursor.close()
    mydb.close()

    if row:
        return jsonify({
            'profilename': row[0],
            'username':    row[1],
            'email':       row[2],
            'profile_pic': row[3]
        })
    return jsonify({})
