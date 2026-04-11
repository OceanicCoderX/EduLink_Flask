# ============================================================
# routes/community.py — Community Page
# Updated: profession tag included in all user queries
# ============================================================

from flask import Blueprint, render_template, request, session, redirect, url_for, jsonify
from db import get_db_connection
from datetime import date
from functools import wraps
import os
from werkzeug.utils import secure_filename

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

    # User's Joined Groups (Approved)
    cursor.execute("""
        SELECT c.group_id, c.group_name, c.group_description, c.admin_id, c.type
        FROM community c
        JOIN group_members gm ON gm.group_id = c.group_id
        WHERE gm.member_id=%s AND gm.status='approved'
    """, (user_id,))
    my_groups = [
        {'group_id': r[0], 'group_name': r[1], 'description': r[2], 'is_admin': (r[3] == user_id), 'type': r[4]}
        for r in cursor.fetchall()
    ]

    # Discovery: All groups
    cursor.execute("""
        SELECT c.group_id, c.group_name, c.group_description, c.type, 
               (SELECT profilename FROM users WHERE user_id = c.admin_id) as admin_name,
               (SELECT COUNT(*) FROM group_members WHERE group_id = c.group_id AND status='approved') as member_count,
               gm.status as my_status
        FROM community c
        LEFT JOIN group_members gm ON gm.group_id = c.group_id AND gm.member_id = %s
        ORDER BY member_count DESC
    """, (user_id,))
    
    discovery = [
        {
            'group_id': r[0], 'group_name': r[1], 'description': r[2], 
            'type': r[3], 'admin_name': r[4], 'member_count': r[5],
            'my_status': r[6]
        }
        for r in cursor.fetchall()
    ]

    # Leaderboard with profession and avatar
    cursor.execute("""
        SELECT u.user_id, u.profilename, u.profile_pic,
               u.profession,
               COALESCE(u.stacks, 0) AS total_stacks,
               u.avatar_id
        FROM users u
        ORDER BY total_stacks DESC
        LIMIT 10
    """)
    leaderboard = [
        {'user_id': r[0], 'name': r[1], 'pic': r[2],
         'profession': r[3] or 'Student', 'stacks': r[4], 'avatar_id': r[5]}
        for r in cursor.fetchall()
    ]

    cursor.execute("SELECT following_id FROM follows WHERE follower_id=%s", (user_id,))
    following_ids = [r[0] for r in cursor.fetchall()]

    cursor.close(); mydb.close()

    return render_template('pages/community.html',
                           user=session,
                           my_groups=my_groups,
                           discovery=discovery,
                           leaderboard=leaderboard,
                           following_ids=following_ids)


@community_bp.route('/group/<int:group_id>')
@login_required
def group_page(group_id):
    user_id = session['user_id']
    mydb    = get_db_connection()
    cursor  = mydb.cursor()

    # Check if user is a member (approved)
    cursor.execute("""
        SELECT gm.status, c.group_name, c.group_description, c.admin_id, c.type
        FROM group_members gm
        JOIN community c ON c.group_id = gm.group_id
        WHERE gm.group_id=%s AND gm.member_id=%s
    """, (group_id, user_id))
    membership = cursor.fetchone()

    if not membership or membership[0] != 'approved':
        cursor.close(); mydb.close()
        return redirect(url_for('community.community', error="unauthorized"))

    # Fetch member count
    cursor.execute("SELECT COUNT(*) FROM group_members WHERE group_id=%s AND status='approved'", (group_id,))
    member_count = cursor.fetchone()[0]

    group_data = {
        'group_id': group_id,
        'group_name': membership[1],
        'description': membership[2],
        'is_admin': (membership[3] == user_id),
        'type': membership[4],
        'member_count': member_count
    }

    # Fetch user's other joined groups for sidebar
    cursor.execute("""
        SELECT c.group_id, c.group_name
        FROM community c
        JOIN group_members gm ON gm.group_id = c.group_id
        WHERE gm.member_id=%s AND gm.status='approved'
    """, (user_id,))
    my_groups = [{'group_id': r[0], 'group_name': r[1]} for r in cursor.fetchall()]

    # Get user details for JS
    cursor.execute("SELECT user_id, profilename FROM users WHERE user_id=%s", (user_id,))
    user_row = cursor.fetchone()
    user_data = {'user_id': user_row[0], 'profilename': user_row[1]}

    cursor.close(); mydb.close()
    return render_template('pages/group.html', group=group_data, my_groups=my_groups, user=user_data)


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
    group_type  = request.form.get('type', 'public') # Added type support

    if not group_name:
        return jsonify({"success": False, "error": "Group name is required"})

    mydb   = get_db_connection()
    cursor = mydb.cursor()

    cursor.execute(
        "INSERT INTO community (group_name, group_description, admin_id, type) VALUES (%s, %s, %s, %s)",
        (group_name, description, user_id, group_type)
    )
    mydb.commit()
    group_id = cursor.lastrowid

    cursor.execute(
        "INSERT INTO group_members (member_id, group_id, join_date, admin_id, status) VALUES (%s, %s, %s, %s, 'approved')",
        (user_id, group_id, date.today(), user_id)
    )
    mydb.commit()
    cursor.close(); mydb.close()

    return jsonify({"success": True, "group_id": group_id})


@community_bp.route('/api/delete-group', methods=['POST'])
@login_required
def delete_group():
    user_id = session['user_id']
    group_id = request.form.get('group_id')
    
    mydb = get_db_connection()
    cursor = mydb.cursor()
    
    cursor.execute("SELECT admin_id FROM community WHERE group_id=%s", (group_id,))
    row = cursor.fetchone()
    
    if not row or row[0] != user_id:
        cursor.close(); mydb.close()
        return jsonify({"success": False, "error": "Unauthorized: Only admin can delete group"})
        
    cursor.execute("DELETE FROM group_members WHERE group_id=%s", (group_id,))
    cursor.execute("DELETE FROM community WHERE group_id=%s", (group_id,))
    mydb.commit()
    
    cursor.close(); mydb.close()
    return jsonify({"success": True})


@community_bp.route('/api/join-group', methods=['POST'])
@login_required
def join_group():
    user_id = session['user_id']
    group_id = request.form.get('group_id')
    
    mydb = get_db_connection()
    cursor = mydb.cursor()
    
    cursor.execute("SELECT type, admin_id FROM community WHERE group_id=%s", (group_id,))
    group = cursor.fetchone()
    if not group:
        cursor.close(); mydb.close()
        return jsonify({"success": False, "error": "Group not found"})
        
    group_type, admin_id = group
    status = 'approved' if group_type == 'public' else 'pending'
    
    cursor.execute(
        "INSERT IGNORE INTO group_members (member_id, group_id, join_date, admin_id, status) VALUES (%s, %s, %s, %s, %s)",
        (user_id, group_id, date.today(), admin_id, status)
    )
    mydb.commit()
    cursor.close(); mydb.close()
    
    return jsonify({"success": True, "status": status})


@community_bp.route('/api/get-group-requests')
@login_required
def get_group_requests():
    user_id = session['user_id']
    mydb = get_db_connection()
    cursor = mydb.cursor()
    
    # Selection: users who have requested to join groups where current user is admin
    cursor.execute("""
        SELECT gm.group_id, c.group_name, gm.member_id, u.profilename, gm.join_date
        FROM group_members gm
        JOIN community c ON c.group_id = gm.group_id
        JOIN users u ON u.user_id = gm.member_id
        WHERE c.admin_id = %s AND gm.status = 'pending'
    """, (user_id,))
    
    reqs = [{
        'group_id': r[0], 'group_name': r[1],
        'user_id': r[2], 'user_name': r[3],
        'date': r[4].strftime("%Y-%m-%d")
    } for r in cursor.fetchall()]
    
    cursor.close(); mydb.close()
    return jsonify(reqs)


@community_bp.route('/api/handle-group-request', methods=['POST'])
@login_required
def handle_group_request():
    admin_id = session['user_id']
    group_id = request.form.get('group_id')
    member_id = request.form.get('user_id')
    action = request.form.get('action') # 'approve' or 'reject'
    
    mydb = get_db_connection()
    cursor = mydb.cursor()
    
    # Auth check
    cursor.execute("SELECT admin_id FROM community WHERE group_id=%s", (group_id,))
    row = cursor.fetchone()
    if not row or row[0] != admin_id:
        cursor.close(); mydb.close()
        return jsonify({"success": False, "error": "Unauthorized"})
        
    if action == 'approve':
        cursor.execute("UPDATE group_members SET status='approved' WHERE group_id=%s AND member_id=%s", (group_id, member_id))
    else:
        cursor.execute("DELETE FROM group_members WHERE group_id=%s AND member_id=%s AND status='pending'", (group_id, member_id))
        
    mydb.commit()
    cursor.close(); mydb.close()
    return jsonify({"success": True})


@community_bp.route('/api/leave-group', methods=['POST'])
@login_required
def leave_group():
    user_id = session['user_id']
    group_id = request.form.get('group_id')
    
    mydb = get_db_connection()
    cursor = mydb.cursor()
    
    # Admin cannot leave without transferring or deleting
    cursor.execute("SELECT admin_id FROM community WHERE group_id=%s", (group_id,))
    row = cursor.fetchone()
    if row and row[0] == user_id:
        cursor.close(); mydb.close()
        return jsonify({"success": False, "error": "Admin cannot leave. Delete the group instead."})
        
    cursor.execute("DELETE FROM group_members WHERE group_id=%s AND member_id=%s", (group_id, user_id))
    mydb.commit()
    cursor.close(); mydb.close()
    return jsonify({"success": True})


@community_bp.route('/api/edit-group', methods=['POST'])
@login_required
def edit_group():
    user_id = session['user_id']
    group_id = request.form.get('group_id')
    name = request.form.get('group_name')
    desc = request.form.get('group_description')
    
    mydb = get_db_connection()
    cursor = mydb.cursor()
    
    cursor.execute("SELECT admin_id FROM community WHERE group_id=%s", (group_id,))
    row = cursor.fetchone()
    if not row or row[0] != user_id:
        cursor.close(); mydb.close()
        return jsonify({"success": False, "error": "Unauthorized"})
        
    cursor.execute("UPDATE community SET group_name=%s, group_description=%s WHERE group_id=%s", (name, desc, group_id))
    mydb.commit()
    cursor.close(); mydb.close()
    return jsonify({"success": True})


ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'zip', 'txt'}
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@community_bp.route('/api/upload-group-file', methods=['POST'])
@login_required
def upload_group_file():
    user_id = session['user_id']
    group_id = request.form.get('group_id')
    
    if not group_id:
        return jsonify({"success": False, "error": "Missing group_id"})

    # Fetch group_name to create folder
    mydb = get_db_connection()
    cursor = mydb.cursor()
    cursor.execute("SELECT group_name FROM community WHERE group_id=%s", (group_id,))
    res = cursor.fetchone()
    if not res:
        cursor.close(); mydb.close()
        return jsonify({"success": False, "error": "Group not found"})
    
    group_name = res[0]
    cursor.close(); mydb.close()

    # Sanitize group_name for folder
    safe_group_name = "".join([c for c in group_name if c.isalnum() or c in (' ', '-', '_')]).strip().replace(' ', '_')
    if not safe_group_name: safe_group_name = f"group_{group_id}"

    if 'file' not in request.files:
        return jsonify({"success": False, "error": "No file part"})
    file = request.files['file']
    if file.filename == '':
        return jsonify({"success": False, "error": "No selected file"})
        
    if file and allowed_file(file.filename):
        original_filename = secure_filename(file.filename)
        # Requirement: <userID_+_File_name>
        unique_filename = f"{user_id}_{original_filename}"
        
        upload_folder = os.path.join('static', 'uploads', 'groups', safe_group_name)
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)
            
        file.save(os.path.join(upload_folder, unique_filename))
        file_url = f"/static/uploads/groups/{safe_group_name}/{unique_filename}"
        
        return jsonify({
            "success": True, 
            "file_url": file_url, 
            "file_name": file.filename,
            "file_type": file.content_type
        })
    return jsonify({"success": False, "error": "File type not allowed"})


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
               u.profession, COALESCE(u.stacks, 0) AS stacks,
               u.avatar_id
        FROM group_members gm
        JOIN users u ON u.user_id = gm.member_id
        WHERE gm.group_id=%s
        ORDER BY stacks DESC
    """, (group_id,))
    rows = cursor.fetchall()
    cursor.close(); mydb.close()

    return jsonify([
        {'user_id': r[0], 'name': r[1], 'pic': r[2],
         'profession': r[3] or 'Student', 'stacks': r[4], 'avatar_id': r[5]}
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
        SELECT cm.message, cm.sent_at, u.profilename, u.user_id, u.profession,
               cm.file_url, cm.file_name, cm.file_type
        FROM community_messages cm
        JOIN users u ON u.user_id = cm.user_id
        WHERE cm.group_id=%s AND cm.subject=%s
        ORDER BY cm.sent_at ASC LIMIT 100
    """, (group_id, subject))
    rows = cursor.fetchall()
    cursor.close(); mydb.close()

    return jsonify([
        {
            'message': r[0], 
            'time': r[1].strftime("%I:%M %p") if r[1] else '',
            'username': r[2], 
            'user_id': r[3], 
            'profession': r[4] or 'Student',
            'file_url': r[5],
            'file_name': r[6],
            'file_type': r[7]
        }
        for r in rows
    ])


@community_bp.route('/api/get-following')
@login_required
def get_following():
    user_id = session['user_id']
    mydb = get_db_connection()
    cursor = mydb.cursor()
    
    cursor.execute("""
        SELECT u.user_id, u.profilename, u.profile_pic, u.profession, u.avatar_id
        FROM users u
        JOIN follows f ON f.following_id = u.user_id
        WHERE f.follower_id = %s
    """, (user_id,))
    
    rows = cursor.fetchall()
    cursor.close(); mydb.close()
    
    return jsonify([
        {'user_id': r[0], 'name': r[1], 'pic': r[2], 'profession': r[3] or 'Student', 'avatar_id': r[4]}
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
        SELECT user_id, profilename, username, profile_pic, profession, avatar_id
        FROM users
        WHERE (profilename LIKE %s OR username LIKE %s) AND user_id != %s
        LIMIT 10
    """, (f'%{query}%', f'%{query}%', user_id))
    rows = cursor.fetchall()
    cursor.close(); mydb.close()

    return jsonify([
        {'user_id': r[0], 'name': r[1], 'username': r[2],
         'pic': r[3], 'profession': r[4] or 'Student', 'avatar_id': r[5]}
        for r in rows
    ])
