# ============================================================
# routes/auth.py — Login, Signup, Logout, Forgot Password
# ============================================================

import os
from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify, flash
from db import get_db_connection

auth_bp = Blueprint('auth', __name__)


# ── Helper ───────────────────────────────────────────────────
def set_user_session(user_row):
    """
    Login ke baad user ki info session mein save karo.
    user_row = DB se aayi tuple (user_id, profile_pic, bg_pic, profilename, username, ...)
    """
    session['user_id']     = user_row[0]
    session['profile_pic'] = user_row[1]
    session['bg_pic']      = user_row[2]
    session['profilename'] = user_row[3]
    session['username']    = user_row[4]
    session['email']       = user_row[6]


# ── Routes ───────────────────────────────────────────────────

@auth_bp.route('/')
def index():
    """Landing page."""
    return render_template('index.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Login page + form handle."""
    if request.method == 'GET':
        # Agar already logged in hai toh dashboard pe bhejo
        if 'user_id' in session:
            return redirect(url_for('dashboard.dashboard'))
        return render_template('login.html')

    # POST — form submit hua
    email    = request.form.get('email')
    password = request.form.get('password')

    mydb   = get_db_connection()
    cursor = mydb.cursor()

    query = "SELECT * FROM users WHERE email=%s AND password=%s"
    cursor.execute(query, (email, password))
    result = cursor.fetchone()

    cursor.close()
    mydb.close()

    if result:
        set_user_session(result)
        return redirect(url_for('dashboard.dashboard'))
    else:
        # Invalid credentials — wapas login pe bhejo with error
        return render_template('login.html', error="Invalid email or password!")


@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    """Signup page + form handle."""
    if request.method == 'GET':
        return render_template('signup.html')

    # POST — form submit hua
    profilename = request.form.get('profilename')
    username    = request.form.get('username')
    whatsapp    = request.form.get('whatsapp')
    email       = request.form.get('email')
    password    = request.form.get('password')
    bio         = request.form.get('bio', '')

    # Default pics (baad mein profile se update honge)
    profile_pic = 'default_user.jpg'
    bg_pic      = 'default_cover.jpg'

    # Handle file uploads if provided
    p1 = request.files.get('profilePicInput')
    b1 = request.files.get('coverPicInput')

    mydb   = get_db_connection()
    cursor = mydb.cursor()

    # Pehle check karo email already exist karta hai ya nahi
    cursor.execute("SELECT user_id FROM users WHERE email=%s", (email,))
    existing = cursor.fetchone()
    if existing:
        cursor.close()
        mydb.close()
        return render_template('signup.html', error="Email already registered!")

    # Insert user
    insert_query = """
        INSERT INTO users
        (profile_pic, background_pic, profilename, username, whatsapp, email, password, bio)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """
    cursor.execute(insert_query, (profile_pic, bg_pic, profilename, username, whatsapp, email, password, bio))
    mydb.commit()

    user_id = cursor.lastrowid  # Naya user ka ID

    # Profile picture save karo (agar diya hai)
    if p1 and p1.filename:
        ext = os.path.splitext(p1.filename)[1]
        profile_pic = f"user{ext}"
        upload_dir = os.path.join('static', 'images', 'users', str(user_id))
        os.makedirs(upload_dir, exist_ok=True)
        p1.save(os.path.join(upload_dir, profile_pic))
        cursor.execute("UPDATE users SET profile_pic=%s WHERE user_id=%s", (profile_pic, user_id))

    # Background picture save karo (agar diya hai)
    if b1 and b1.filename:
        ext = os.path.splitext(b1.filename)[1]
        bg_pic = f"cover{ext}"
        bg_dir = os.path.join('static', 'images', 'background', str(user_id))
        os.makedirs(bg_dir, exist_ok=True)
        b1.save(os.path.join(bg_dir, bg_pic))
        cursor.execute("UPDATE users SET background_pic=%s WHERE user_id=%s", (bg_pic, user_id))

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

    email = request.form.get('email')
    mydb   = get_db_connection()
    cursor = mydb.cursor()
    cursor.execute("SELECT user_id FROM users WHERE email=%s", (email,))
    result = cursor.fetchone()
    cursor.close()
    mydb.close()

    if result:
        # Real project mein yahan OTP email bhejte — abhi simple redirect
        return render_template('update_password.html', email=email)
    else:
        return render_template('forgot_password.html', error="Email not found!")


@auth_bp.route('/update-password', methods=['POST'])
def update_password():
    """New password save karo."""
    email        = request.form.get('email')
    new_password = request.form.get('new_password')

    mydb   = get_db_connection()
    cursor = mydb.cursor()
    cursor.execute("UPDATE users SET password=%s WHERE email=%s", (new_password, email))
    mydb.commit()
    cursor.close()
    mydb.close()

    return redirect(url_for('auth.login'))
