# ============================================================
# routes/notebook.py — Notebook Page + Notes CRUD API
# user_id se linked — har user ke apne notes
# ============================================================

from flask import Blueprint, render_template, request, session, redirect, url_for, jsonify
from db import get_db_connection
from datetime import date
from functools import wraps

notebook_bp = Blueprint('notebook', __name__)


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated


@notebook_bp.route('/notebook')
@login_required
def notebook():
    return render_template('pages/notebook.html', user=session)


@notebook_bp.route('/api/notes', methods=['GET'])
@login_required
def get_notes():
    """
    Logged-in user ke saare notes fetch karo.
    Optional filter: ?category=physics
    """
    user_id  = session['user_id']
    category = request.args.get('category', 'all')  # URL se category filter

    mydb   = get_db_connection()
    cursor = mydb.cursor()

    if category == 'all':
        cursor.execute(
            "SELECT * FROM notes WHERE user_id=%s ORDER BY created_date DESC",
            (user_id,)
        )
    else:
        cursor.execute(
            "SELECT * FROM notes WHERE user_id=%s AND category=%s ORDER BY created_date DESC",
            (user_id, category)
        )

    rows = cursor.fetchall()
    cursor.close()
    mydb.close()

    notes_list = []
    for n in rows:
        notes_list.append({
            'notes_id':          n[0],
            'notes_title':       n[1],
            'notes_description': n[2],
            'created_date':      str(n[3]),
            'user_id':           n[4],
            'category':          n[5] if len(n) > 5 else 'general',
            'tags':              n[6] if len(n) > 6 else ''
        })

    return jsonify(notes_list)


@notebook_bp.route('/api/save-note', methods=['POST'])
@login_required
def save_note():
    """Naya note save karo."""
    user_id     = session['user_id']
    title       = request.form.get('notes_title', 'Untitled Note')
    description = request.form.get('notes_description', '')
    category    = request.form.get('category', 'general')
    tags        = request.form.get('tags', '')
    today       = date.today()

    mydb   = get_db_connection()
    cursor = mydb.cursor()

    cursor.execute("""
        INSERT INTO notes (notes_title, notes_description, created_date, user_id, category, tags)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (title, description, today, user_id, category, tags))

    mydb.commit()
    note_id = cursor.lastrowid
    cursor.close()
    mydb.close()

    return jsonify({"success": True, "notes_id": note_id})


@notebook_bp.route('/api/update-note', methods=['POST'])
@login_required
def update_note():
    """Existing note update karo."""
    user_id     = session['user_id']
    note_id     = request.form.get('notes_id')
    title       = request.form.get('notes_title', 'Untitled Note')
    description = request.form.get('notes_description', '')
    category    = request.form.get('category', 'general')
    tags        = request.form.get('tags', '')

    mydb   = get_db_connection()
    cursor = mydb.cursor()

    cursor.execute("""
        UPDATE notes
        SET notes_title=%s, notes_description=%s, category=%s, tags=%s
        WHERE notes_id=%s AND user_id=%s
    """, (title, description, category, tags, note_id, user_id))

    mydb.commit()
    cursor.close()
    mydb.close()

    return jsonify({"success": True})


@notebook_bp.route('/api/delete-note', methods=['POST'])
@login_required
def delete_note():
    """Note delete karo."""
    user_id = session['user_id']
    note_id = request.form.get('notes_id')

    mydb   = get_db_connection()
    cursor = mydb.cursor()
    cursor.execute("DELETE FROM notes WHERE notes_id=%s AND user_id=%s", (note_id, user_id))
    mydb.commit()
    cursor.close()
    mydb.close()

    return jsonify({"success": True})
