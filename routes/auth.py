# ============================================================
# routes/auth.py — Login, Signup, Logout, Forgot Password
# Updated: profession tag, password hashing, daily login stack
# ============================================================

import os
from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from db import get_db_connection
from helpers.stacks import handle_daily_login, log_activity

auth_bp = Blueprint('auth', __name__)


# ── Helper ───────────────────────────────────────────────────
def set_user_session(user_row):
    """
    Login ke baad user ki info session mein save karo.
    user_row columns:
      0:user_id, 1:profile_pic, 2:bg_pic, 3:profilename, 4:username,
      5:whatsapp, 6:email, 7:password, 8:bio, 9:created_date,
      10:profession, 11:stacks, 12:streak, ...
    """
    session['user_id']     = user_row[0]
    session['profile_pic'] = user_row[1]
    session['bg_pic']      = user_row[2]
    session['profilename'] = user_row[3]
    session['username']    = user_row[4]
    session['email']       = user_row[6]
    session['profession']  = user_row[10] if len(user_row) > 10 else 'Student'
    session['stacks']      = user_row[11] if len(user_row) > 11 else 0
    session['streak']      = user_row[12] if len(user_row) > 12 else 0


# ── Routes ───────────────────────────────────────────────────

@auth_bp.route('/')
def index():
    """Landing page."""
    return render_template('index.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Login page + form handle."""
    if request.method == 'GET':
        if 'user_id' in session:
            return redirect(url_for('dashboard.dashboard'))
        return render_template('login.html')

    # POST — form submit
    email    = request.form.get('email', '').strip()
    password = request.form.get('password', '')

    mydb   = get_db_connection()
    cursor = mydb.cursor()

    cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
    result = cursor.fetchone()

    cursor.close()
    mydb.close()

    if result:
        stored_password = result[7]  # password column

        # Check hashed password first, then fall back to plain text
        password_ok = False
        if stored_password.startswith('pbkdf2:') or stored_password.startswith('scrypt:'):
            password_ok = check_password_hash(stored_password, password)
        else:
            # Plain text — compare directly AND upgrade to hash
            password_ok = (stored_password == password)
            if password_ok:
                # Auto-upgrade to hashed password
                hashed = generate_password_hash(password)
                mydb2   = get_db_connection()
                cursor2 = mydb2.cursor()
                cursor2.execute("UPDATE users SET password=%s WHERE user_id=%s",
                                (hashed, result[0]))
                mydb2.commit()
                cursor2.close()
                mydb2.close()

        if password_ok:
            set_user_session(result)
            # Award daily login stack
            handle_daily_login(result[0])
            return redirect(url_for('dashboard.dashboard'))

    return render_template('login.html', error="Invalid email or password!")


@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    """Signup page + form handle."""
    if request.method == 'GET':
        return render_template('signup.html')

    # POST
    profilename = request.form.get('profilename', '').strip()
    username    = request.form.get('username', '').strip().lower()
    whatsapp    = request.form.get('whatsapp', '').strip()
    email       = request.form.get('email', '').strip().lower()
    password    = request.form.get('password', '')
    bio         = request.form.get('bio', '').strip()
    profession  = request.form.get('profession', 'Student')

    # Hash the password immediately
    hashed_password = generate_password_hash(password)

    # Default pics
    profile_pic = 'default_user.jpg'
    bg_pic      = 'default_cover.jpg'

    mydb   = get_db_connection()
    cursor = mydb.cursor()

    # Check email exists
    cursor.execute("SELECT user_id FROM users WHERE email=%s", (email,))
    if cursor.fetchone():
        cursor.close()
        mydb.close()
        return render_template('signup.html', error="Email already registered!")

    # Check username exists
    cursor.execute("SELECT user_id FROM users WHERE username=%s", (username,))
    if cursor.fetchone():
        cursor.close()
        mydb.close()
        return render_template('signup.html', error="Username already taken!")

    # Insert user
    cursor.execute("""
        INSERT INTO users
        (profile_pic, background_pic, profilename, username, whatsapp, email, password, bio, profession)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (profile_pic, bg_pic, profilename, username, whatsapp, email, hashed_password, bio, profession))
    mydb.commit()
    user_id = cursor.lastrowid

    # Handle profile picture upload
    p1 = request.files.get('profilePicInput')
    if p1 and p1.filename:
        ext = os.path.splitext(p1.filename)[1]
        profile_pic = f"user{ext}"
        upload_dir  = os.path.join('static', 'images', 'users', str(user_id))
        os.makedirs(upload_dir, exist_ok=True)
        p1.save(os.path.join(upload_dir, profile_pic))
        cursor.execute("UPDATE users SET profile_pic=%s WHERE user_id=%s", (profile_pic, user_id))

    # Handle background picture upload
    b1 = request.files.get('coverPicInput')
    if b1 and b1.filename:
        ext    = os.path.splitext(b1.filename)[1]
        bg_pic = f"cover{ext}"
        bg_dir = os.path.join('static', 'images', 'background', str(user_id))
        os.makedirs(bg_dir, exist_ok=True)
        b1.save(os.path.join(bg_dir, bg_pic))
        cursor.execute("UPDATE users SET background_pic=%s WHERE user_id=%s", (bg_pic, user_id))

    # Log first activity (safe — table may not exist before migration)
    try:
        cursor.execute(
            "INSERT INTO activity_log (user_id, action_type, action_desc) VALUES (%s, %s, %s)",
            (user_id, 'signup', 'Joined EduLink!')
        )
    except Exception:
        pass

    mydb.commit()
    cursor.close()
    mydb.close()

    return redirect(url_for('auth.login'))


@auth_bp.route('/logout')
def logout():
    """Session clear karo aur login pe bhejo."""
    session.clear()
    return redirect(url_for('auth.login'))


@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """Forgot password page."""
    if request.method == 'GET':
        return render_template('forgot_password.html')

    email  = request.form.get('email', '').strip()
    mydb   = get_db_connection()
    cursor = mydb.cursor()
    cursor.execute("SELECT user_id FROM users WHERE email=%s", (email,))
    result = cursor.fetchone()
    cursor.close()
    mydb.close()

    if result:
        return render_template('update_password.html', email=email)
    else:
        return render_template('forgot_password.html', error="Email not found!")


@auth_bp.route('/update-password', methods=['POST'])
def update_password():
    """New password save karo (hashed)."""
    email        = request.form.get('email', '')
    new_password = request.form.get('new_password', '')

    hashed = generate_password_hash(new_password)

    mydb   = get_db_connection()
    cursor = mydb.cursor()
    cursor.execute("UPDATE users SET password=%s WHERE email=%s", (hashed, email))
    mydb.commit()
    cursor.close()
    mydb.close()

    return redirect(url_for('auth.login'))
