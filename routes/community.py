# ============================================================
# routes/community.py — Community Page
# Updated: profession tag included in all user queries
# ============================================================

from flask import Blueprint, render_template, request, session, redirect, url_for, jsonify
from db import get_db_connection
from datetime import date
from functools import wraps

community_bp = Blueprint('community', __name__)


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated


@community_bp.route('/community')
@login_required
def community():
    user_id = session['user_id']
    mydb    = get_db_connection()
    cursor  = mydb.cursor()

    cursor.execute("""
        SELECT c.group_id, c.group_name, c.group_description, c.admin_id
        FROM community c
        JOIN group_members gm ON gm.group_id = c.group_id
        WHERE gm.member_id=%s
    """, (user_id,))
    my_groups = [
        {'group_id': r[0], 'group_name': r[1], 'description': r[2], 'is_admin': (r[3] == user_id)}
        for r in cursor.fetchall()
    ]

    # Leaderboard with profession
    cursor.execute("""
        SELECT u.user_id, u.profilename, u.profile_pic,
               u.profession,
               COALESCE(u.stacks, 0) AS total_stacks
        FROM users u
        ORDER BY total_stacks DESC
        LIMIT 10
    """)
    leaderboard = [
        {'user_id': r[0], 'name': r[1], 'pic': r[2],
         'profession': r[3] or 'Student', 'stacks': r[4]}
        for r in cursor.fetchall()
    ]

    cursor.execute("SELECT following_id FROM follows WHERE follower_id=%s", (user_id,))
    following_ids = [r[0] for r in cursor.fetchall()]

    cursor.close(); mydb.close()

    return render_template('pages/community.html',
                           user=session,
                           my_groups=my_groups,
                           leaderboard=leaderboard,
                           following_ids=following_ids)


@community_bp.route('/api/get-posts')
@login_required
def get_posts():
    subject = request.args.get('subject', 'all')
    mydb    = get_db_connection()
    cursor  = mydb.cursor()

    base = """
        SELECT p.post_id, p.content, p.subject, p.created_at,
               u.profilename, u.user_id, u.profession,
               (SELECT COUNT(*) FROM post_likes pl WHERE pl.post_id=p.post_id) AS likes,
               (SELECT COUNT(*) FROM post_comments pc WHERE pc.post_id=p.post_id) AS comments
        FROM posts p JOIN users u ON u.user_id=p.user_id
    """
    if subject == 'all':
        cursor.execute(base + " ORDER BY p.created_at DESC LIMIT 20")
    else:
        cursor.execute(base + " WHERE p.subject=%s ORDER BY p.created_at DESC LIMIT 20", (subject,))

    rows = cursor.fetchall()
    cursor.close(); mydb.close()

    posts = [{
        'post_id':   r[0], 'content': r[1], 'subject': r[2],
        'time':      r[3].strftime("%b %d, %Y") if r[3] else '',
        'username':  r[4], 'user_id': r[5],
        'profession': r[6] or 'Student',
        'likes':     r[7], 'comments': r[8]
    } for r in rows]
    return jsonify(posts)


@community_bp.route('/api/create-post', methods=['POST'])
@login_required
def create_post():
    user_id = session['user_id']
    content = request.form.get('content', '').strip()
    subject = request.form.get('subject', 'general')

    if not content:
        return jsonify({"success": False, "error": "Post cannot be empty"})

    mydb   = get_db_connection()
    cursor = mydb.cursor()
    cursor.execute(
        "INSERT INTO posts (user_id, content, subject) VALUES (%s, %s, %s)",
        (user_id, content, subject)
    )
    mydb.commit()
    post_id = cursor.lastrowid
    cursor.close(); mydb.close()

    return jsonify({"success": True, "post_id": post_id})


@community_bp.route('/api/like-post', methods=['POST'])
@login_required
def like_post():
    user_id = session['user_id']
    post_id = request.form.get('post_id')

    mydb   = get_db_connection()
    cursor = mydb.cursor()

    cursor.execute(
        "SELECT like_id FROM post_likes WHERE post_id=%s AND user_id=%s",
        (post_id, user_id)
    )
    existing = cursor.fetchone()

    if existing:
        cursor.execute("DELETE FROM post_likes WHERE post_id=%s AND user_id=%s", (post_id, user_id))
        liked = False
    else:
        cursor.execute("INSERT INTO post_likes (post_id, user_id) VALUES (%s, %s)", (post_id, user_id))
        liked = True

    mydb.commit()

    cursor.execute("SELECT COUNT(*) FROM post_likes WHERE post_id=%s", (post_id,))
    count = cursor.fetchone()[0]
    cursor.close(); mydb.close()

    return jsonify({"success": True, "liked": liked, "count": count})


@community_bp.route('/api/create-group', methods=['POST'])
@login_required
def create_group():
    user_id     = session['user_id']
    group_name  = request.form.get('group_name')
    description = request.form.get('group_description', '')

    mydb   = get_db_connection()
    cursor = mydb.cursor()

    cursor.execute(
        "INSERT INTO community (group_name, group_description, admin_id, group_member_id) VALUES (%s, %s, %s, %s)",
        (group_name, description, user_id, user_id)
    )
    mydb.commit()
    group_id = cursor.lastrowid

    cursor.execute(
        "INSERT INTO group_members (member_id, group_id, join_date, admin_id) VALUES (%s, %s, %s, %s)",
        (user_id, group_id, date.today(), user_id)
    )
    mydb.commit()
    cursor.close(); mydb.close()

    return jsonify({"success": True, "group_id": group_id})


@community_bp.route('/api/add-group-member', methods=['POST'])
@login_required
def add_group_member():
    user_id   = session['user_id']
    group_id  = request.form.get('group_id')
    member_id = request.form.get('member_id')

    mydb   = get_db_connection()
    cursor = mydb.cursor()

    cursor.execute("SELECT admin_id FROM community WHERE group_id=%s", (group_id,))
    row = cursor.fetchone()
    if not row or row[0] != user_id:
        cursor.close(); mydb.close()
        return jsonify({"success": False, "error": "Only admin can add members"})

    cursor.execute(
        "INSERT IGNORE INTO group_members (member_id, group_id, join_date, admin_id) VALUES (%s, %s, %s, %s)",
        (member_id, group_id, date.today(), user_id)
    )
    mydb.commit()
    cursor.close(); mydb.close()

    return jsonify({"success": True})


@community_bp.route('/api/remove-group-member', methods=['POST'])
@login_required
def remove_group_member():
    user_id   = session['user_id']
    group_id  = request.form.get('group_id')
    member_id = request.form.get('member_id')

    mydb   = get_db_connection()
    cursor = mydb.cursor()

    cursor.execute("SELECT admin_id FROM community WHERE group_id=%s", (group_id,))
    row = cursor.fetchone()
    if not row or row[0] != user_id:
        cursor.close(); mydb.close()
        return jsonify({"success": False, "error": "Only admin can remove members"})

    cursor.execute(
        "DELETE FROM group_members WHERE group_id=%s AND member_id=%s",
        (group_id, member_id)
    )
    mydb.commit()
    cursor.close(); mydb.close()

    return jsonify({"success": True})


@community_bp.route('/api/get-group-members')
@login_required
def get_group_members():
    group_id = request.args.get('group_id')
    mydb     = get_db_connection()
    cursor   = mydb.cursor()

    cursor.execute("""
        SELECT u.user_id, u.profilename, u.profile_pic,
               u.profession, COALESCE(u.stacks, 0) AS stacks
        FROM group_members gm
        JOIN users u ON u.user_id = gm.member_id
        WHERE gm.group_id=%s
        ORDER BY stacks DESC
    """, (group_id,))
    rows = cursor.fetchall()
    cursor.close(); mydb.close()

    return jsonify([
        {'user_id': r[0], 'name': r[1], 'pic': r[2],
         'profession': r[3] or 'Student', 'stacks': r[4]}
        for r in rows
    ])


@community_bp.route('/api/get-chat-history')
@login_required
def get_chat_history():
    group_id = request.args.get('group_id')
    subject  = request.args.get('subject', 'general')
    mydb     = get_db_connection()
    cursor   = mydb.cursor()

    cursor.execute("""
        SELECT cm.message, cm.sent_at, u.profilename, u.user_id, u.profession
        FROM community_messages cm
        JOIN users u ON u.user_id = cm.user_id
        WHERE cm.group_id=%s AND cm.subject=%s
        ORDER BY cm.sent_at ASC LIMIT 50
    """, (group_id, subject))
    rows = cursor.fetchall()
    cursor.close(); mydb.close()

    return jsonify([
        {'message': r[0], 'time': r[1].strftime("%I:%M %p"),
         'username': r[2], 'user_id': r[3], 'profession': r[4] or 'Student'}
        for r in rows
    ])


@community_bp.route('/api/follow', methods=['POST'])
@login_required
def follow_user():
    follower_id  = session['user_id']
    following_id = request.form.get('user_id')

    if str(follower_id) == str(following_id):
        return jsonify({"success": False, "error": "Cannot follow yourself"})

    mydb   = get_db_connection()
    cursor = mydb.cursor()
    cursor.execute(
        "INSERT IGNORE INTO follows (follower_id, following_id) VALUES (%s, %s)",
        (follower_id, following_id)
    )
    mydb.commit()
    cursor.close(); mydb.close()

    return jsonify({"success": True, "action": "followed"})


@community_bp.route('/api/unfollow', methods=['POST'])
@login_required
def unfollow_user():
    follower_id  = session['user_id']
    following_id = request.form.get('user_id')

    mydb   = get_db_connection()
    cursor = mydb.cursor()
    cursor.execute(
        "DELETE FROM follows WHERE follower_id=%s AND following_id=%s",
        (follower_id, following_id)
    )
    mydb.commit()
    cursor.close(); mydb.close()

    return jsonify({"success": True, "action": "unfollowed"})


@community_bp.route('/api/search-users')
@login_required
def search_users():
    query   = request.args.get('q', '')
    user_id = session['user_id']
    mydb    = get_db_connection()
    cursor  = mydb.cursor()

    cursor.execute("""
        SELECT user_id, profilename, username, profile_pic, profession
        FROM users
        WHERE (profilename LIKE %s OR username LIKE %s) AND user_id != %s
        LIMIT 10
    """, (f'%{query}%', f'%{query}%', user_id))
    rows = cursor.fetchall()
    cursor.close(); mydb.close()

    return jsonify([
        {'user_id': r[0], 'name': r[1], 'username': r[2],
         'pic': r[3], 'profession': r[4] or 'Student'}
        for r in rows
    ])
