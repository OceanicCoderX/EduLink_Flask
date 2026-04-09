# ============================================================
# routes/friends.py — Friends Stack / Leaderboard Page
# Updated: profession tag in all user data
# ============================================================

from flask import Blueprint, render_template, request, session, redirect, url_for, jsonify
from db import get_db_connection
from functools import wraps

friends_bp = Blueprint('friends', __name__)


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated


def get_rank_and_badge(stacks):
    """Stacks ke hisaab se rank aur badge determine karo."""
    if stacks >= 500:  return "Legend",       "🏆"
    if stacks >= 200:  return "Expert",        "💎"
    if stacks >= 100:  return "Advanced",      "🥇"
    if stacks >= 50:   return "Intermediate",  "🥈"
    if stacks >= 20:   return "Learner",       "🥉"
    return "Beginner", "🌱"


@friends_bp.route('/friends-stack')
@login_required
def friends_stack():
    user_id = session['user_id']
    mydb    = get_db_connection()
    cursor  = mydb.cursor()

    # People I follow (with centralized stacks)
    cursor.execute("""
        SELECT u.user_id, u.profilename, u.username, u.profile_pic, u.bio,
               u.profession,
               COALESCE(u.stacks, 0)           AS total_stacks,
               COALESCE(SUM(f.sessions_count),0) AS total_sessions,
               COALESCE(SUM(f.duration_minutes),0) AS total_minutes
        FROM follows fl
        JOIN users u ON u.user_id = fl.following_id
        LEFT JOIN focus f ON f.user_id = u.user_id
        WHERE fl.follower_id=%s
        GROUP BY u.user_id
        ORDER BY total_stacks DESC
    """, (user_id,))
    following_rows = cursor.fetchall()

    # My followers (ids only for is_following_back check)
    cursor.execute("""
        SELECT u.user_id FROM follows fl
        JOIN users u ON u.user_id = fl.follower_id
        WHERE fl.following_id=%s
    """, (user_id,))
    follower_ids = {r[0] for r in cursor.fetchall()}

    cursor.close(); mydb.close()

    following_list = []
    for r in following_rows:
        stacks      = int(r[6])
        rank, badge = get_rank_and_badge(stacks)
        following_list.append({
            'user_id':             r[0],
            'name':                r[1],
            'username':            r[2],
            'pic':                 r[3],
            'bio':                 r[4] or '',
            'profession':          r[5] or 'Student',
            'stacks':              stacks,
            'sessions':            int(r[7]),
            'hours':               round(float(r[8]) / 60, 1),
            'rank':                rank,
            'badge':               badge,
            'is_following_back':   r[0] in follower_ids
        })

    return render_template('pages/friends_stack.html',
                           user=session,
                           following_list=following_list)


@friends_bp.route('/api/get-user-profile/<int:target_user_id>')
@login_required
def get_user_profile(target_user_id):
    """Public profile fetch for any user."""
    mydb   = get_db_connection()
    cursor = mydb.cursor()

    cursor.execute("""
        SELECT u.user_id, u.profilename, u.username, u.profile_pic, u.bio,
               u.profession,
               COALESCE(u.stacks, 0)            AS stacks,
               COALESCE(SUM(f.sessions_count),0) AS sessions,
               COALESCE(SUM(f.duration_minutes),0) AS minutes,
               (SELECT COUNT(*) FROM follows WHERE following_id=u.user_id) AS followers,
               (SELECT COUNT(*) FROM follows WHERE follower_id=u.user_id)  AS following
        FROM users u
        LEFT JOIN focus f ON f.user_id = u.user_id
        WHERE u.user_id=%s
        GROUP BY u.user_id
    """, (target_user_id,))
    row = cursor.fetchone()
    cursor.close(); mydb.close()

    if not row:
        return jsonify({"error": "User not found"}), 404

    stacks      = int(row[6])
    rank, badge = get_rank_and_badge(stacks)

    return jsonify({
        'user_id':    row[0],
        'name':       row[1],
        'username':   row[2],
        'pic':        row[3],
        'bio':        row[4] or '',
        'profession': row[5] or 'Student',
        'stacks':     stacks,
        'sessions':   int(row[7]),
        'hours':      round(float(row[8]) / 60, 1),
        'rank':       rank,
        'badge':      badge,
        'followers':  row[9],
        'following':  row[10]
    })


@friends_bp.route('/api/global-leaderboard')
@login_required
def global_leaderboard():
    """Top 20 users by stacks for leaderboard."""
    mydb   = get_db_connection()
    cursor = mydb.cursor()

    cursor.execute("""
        SELECT user_id, profilename, profile_pic, profession,
               COALESCE(stacks, 0) AS total_stacks, streak
        FROM users
        ORDER BY total_stacks DESC
        LIMIT 20
    """)
    rows = cursor.fetchall()
    cursor.close(); mydb.close()

    result = []
    for i, r in enumerate(rows):
        stacks      = int(r[4])
        rank, badge = get_rank_and_badge(stacks)
        result.append({
            'position':   i + 1,
            'user_id':    r[0],
            'name':       r[1],
            'pic':        r[2],
            'profession': r[3] or 'Student',
            'stacks':     stacks,
            'streak':     int(r[5]) if r[5] else 0,
            'rank':       rank,
            'badge':      badge
        })

    return jsonify(result)
