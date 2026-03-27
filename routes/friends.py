# ============================================================
# routes/friends.py — Friends Stack Page
# Yahan friends ke ranks, stacks, badges sab dikhta hai
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
    """
    Stacks ke hisaab se rank aur badge determine karo.
    Jaisa ek gaming system hota hai.
    """
    if stacks >= 500:
        return "Legend", "🏆"
    elif stacks >= 200:
        return "Expert", "💎"
    elif stacks >= 100:
        return "Advanced", "🥇"
    elif stacks >= 50:
        return "Intermediate", "🥈"
    elif stacks >= 20:
        return "Learner", "🥉"
    else:
        return "Beginner", "🌱"


@friends_bp.route('/friends-stack')
@login_required
def friends_stack():
    """
    Friends Stack page — logged-in user ke followers/following ki
    full profile dikhao: stacks, rank, badge, contributions.
    """
    user_id = session['user_id']
    mydb    = get_db_connection()
    cursor  = mydb.cursor()

    # Jinhe main follow karta hoon unki info
    cursor.execute("""
        SELECT u.user_id, u.profilename, u.username, u.profile_pic, u.bio,
               COALESCE(SUM(f.stacks_earned), 0) AS total_stacks,
               COALESCE(SUM(f.sessions_count), 0) AS total_sessions,
               COALESCE(SUM(f.duration_minutes), 0) AS total_minutes
        FROM follows fl
        JOIN users u ON u.user_id = fl.following_id
        LEFT JOIN focus f ON f.user_id = u.user_id
        WHERE fl.follower_id=%s
        GROUP BY u.user_id
        ORDER BY total_stacks DESC
    """, (user_id,))
    following_rows = cursor.fetchall()

    # Mere followers
    cursor.execute("""
        SELECT u.user_id, u.profilename, u.profile_pic
        FROM follows fl
        JOIN users u ON u.user_id = fl.follower_id
        WHERE fl.following_id=%s
    """, (user_id,))
    follower_ids = [r[0] for r in cursor.fetchall()]

    cursor.close()
    mydb.close()

    # Process following list with rank/badge
    following_list = []
    for r in following_rows:
        stacks = r[5]
        rank, badge = get_rank_and_badge(stacks)
        following_list.append({
            'user_id':       r[0],
            'name':          r[1],
            'username':      r[2],
            'pic':           r[3],
            'bio':           r[4] or '',
            'stacks':        stacks,
            'sessions':      r[6],
            'hours':         round(r[7] / 60, 1),
            'rank':          rank,
            'badge':         badge,
            'is_following_back': r[0] in follower_ids
        })

    return render_template('pages/friends_stack.html',
                           user=session,
                           following_list=following_list)


@friends_bp.route('/api/get-user-profile/<int:target_user_id>')
@login_required
def get_user_profile(target_user_id):
    """
    Kisi bhi user ka public profile fetch karo.
    Community page se click karke aayenge.
    """
    mydb   = get_db_connection()
    cursor = mydb.cursor()

    cursor.execute("""
        SELECT u.user_id, u.profilename, u.username, u.profile_pic, u.bio,
               COALESCE(SUM(f.stacks_earned), 0) AS stacks,
               COALESCE(SUM(f.sessions_count), 0) AS sessions,
               COALESCE(SUM(f.duration_minutes), 0) AS minutes,
               (SELECT COUNT(*) FROM follows WHERE following_id=u.user_id) AS followers,
               (SELECT COUNT(*) FROM follows WHERE follower_id=u.user_id) AS following
        FROM users u
        LEFT JOIN focus f ON f.user_id = u.user_id
        WHERE u.user_id=%s
        GROUP BY u.user_id
    """, (target_user_id,))
    row = cursor.fetchone()
    cursor.close()
    mydb.close()

    if not row:
        return jsonify({"error": "User not found"}), 404

    stacks = row[5]
    rank, badge = get_rank_and_badge(stacks)

    return jsonify({
        'user_id':   row[0],
        'name':      row[1],
        'username':  row[2],
        'pic':       row[3],
        'bio':       row[4] or '',
        'stacks':    stacks,
        'sessions':  row[6],
        'hours':     round(row[7] / 60, 1),
        'rank':      rank,
        'badge':     badge,
        'followers': row[8],
        'following': row[9]
    })
