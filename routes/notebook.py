# ============================================================
# routes/notebook.py — Notebook + File Upload/Share API
# Rule 6: PDF, Word, PPT, Excel upload + in-site preview
# ============================================================

import os
import uuid
from flask import (Blueprint, render_template, request, session,
                   redirect, url_for, jsonify, send_from_directory, abort)
from db import get_db_connection
from datetime import date
from functools import wraps
from helpers.stacks import log_activity

notebook_bp = Blueprint('notebook', __name__)

ALLOWED_EXTENSIONS = {'pdf', 'docx', 'pptx', 'xlsx', 'txt', 'png', 'jpg', 'jpeg'}
UPLOAD_BASE = os.path.join('static', 'uploads')


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_file_type(filename):
    ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else 'txt'
    mapping = {
        'pdf':  'pdf',
        'docx': 'word',
        'doc':  'word',
        'pptx': 'ppt',
        'ppt':  'ppt',
        'xlsx': 'excel',
        'xls':  'excel',
        'txt':  'text',
        'png':  'image',
        'jpg':  'image',
        'jpeg': 'image',
    }
    return mapping.get(ext, 'file')


# ── Pages ────────────────────────────────────────────────────

@notebook_bp.route('/notebook')
@login_required
def notebook():
    return render_template('pages/notebook.html', user=session)


# ── Notes API ────────────────────────────────────────────────

@notebook_bp.route('/api/notes', methods=['GET'])
@login_required
def get_notes():
    user_id  = session['user_id']
    category = request.args.get('category', 'all')

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
    cursor.close(); mydb.close()

    notes_list = [{
        'notes_id':          n[0],
        'notes_title':       n[1],
        'notes_description': n[2],
        'created_date':      str(n[3]),
        'user_id':           n[4],
        'category':          n[5] if len(n) > 5 else 'general',
        'tags':              n[6] if len(n) > 6 else ''
    } for n in rows]

    return jsonify(notes_list)


@notebook_bp.route('/api/save-note', methods=['POST'])
@login_required
def save_note():
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
    cursor.close(); mydb.close()

    log_activity(user_id, 'note', f'Created note "{title}"')
    return jsonify({"success": True, "notes_id": note_id})


@notebook_bp.route('/api/update-note', methods=['POST'])
@login_required
def update_note():
    user_id     = session['user_id']
    note_id     = request.form.get('notes_id')
    title       = request.form.get('notes_title', 'Untitled Note')
    description = request.form.get('notes_description', '')
    category    = request.form.get('category', 'general')
    tags        = request.form.get('tags', '')

    mydb   = get_db_connection()
    cursor = mydb.cursor()

    cursor.execute("""
        UPDATE notes SET notes_title=%s, notes_description=%s, category=%s, tags=%s
        WHERE notes_id=%s AND user_id=%s
    """, (title, description, category, tags, note_id, user_id))

    mydb.commit()
    cursor.close(); mydb.close()

    return jsonify({"success": True})


@notebook_bp.route('/api/delete-note', methods=['POST'])
@login_required
def delete_note():
    user_id = session['user_id']
    note_id = request.form.get('notes_id')

    mydb   = get_db_connection()
    cursor = mydb.cursor()
    cursor.execute("DELETE FROM notes WHERE notes_id=%s AND user_id=%s", (note_id, user_id))
    mydb.commit()
    cursor.close(); mydb.close()

    return jsonify({"success": True})


# ── File Upload API ──────────────────────────────────────────

@notebook_bp.route('/api/upload-file', methods=['POST'])
@login_required
def upload_file():
    """Upload a file (PDF, Word, PPT, Excel, image)."""
    user_id = session['user_id']

    if 'file' not in request.files:
        return jsonify({"success": False, "error": "No file provided"})

    f = request.files['file']
    if not f or not f.filename:
        return jsonify({"success": False, "error": "Empty filename"})

    if not allowed_file(f.filename):
        return jsonify({"success": False, "error": "File type not allowed"})

    original_name = f.filename
    ext           = original_name.rsplit('.', 1)[1].lower()
    unique_name   = f"{uuid.uuid4().hex}.{ext}"
    file_type     = get_file_type(original_name)

    # Save to static/uploads/<user_id>/
    user_upload_dir = os.path.join(UPLOAD_BASE, str(user_id))
    os.makedirs(user_upload_dir, exist_ok=True)
    save_path = os.path.join(user_upload_dir, unique_name)
    f.save(save_path)

    file_size = os.path.getsize(save_path)
    rel_path  = f"uploads/{user_id}/{unique_name}"

    mydb   = get_db_connection()
    cursor = mydb.cursor()

    cursor.execute("""
        INSERT INTO uploaded_files
        (user_id, file_name, file_original, file_type, file_path, file_size)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (user_id, unique_name, original_name, file_type, rel_path, file_size))

    mydb.commit()
    file_id = cursor.lastrowid
    cursor.close(); mydb.close()

    log_activity(user_id, 'upload', f'Uploaded "{original_name}"')

    return jsonify({
        "success":       True,
        "file_id":       file_id,
        "file_name":     unique_name,
        "file_original": original_name,
        "file_type":     file_type,
        "file_path":     rel_path,
        "file_size":     file_size
    })


@notebook_bp.route('/api/get-files')
@login_required
def get_files():
    """Get all uploaded files for the logged-in user."""
    user_id = session['user_id']
    include_shared = request.args.get('shared', 'false') == 'true'

    mydb   = get_db_connection()
    cursor = mydb.cursor()

    if include_shared:
        cursor.execute("""
            SELECT f.file_id, f.user_id, f.file_name, f.file_original,
                   f.file_type, f.file_path, f.file_size, f.shared, f.uploaded_at,
                   u.profilename, u.profession
            FROM uploaded_files f
            JOIN users u ON u.user_id = f.user_id
            WHERE f.user_id=%s OR f.shared=1
            ORDER BY f.uploaded_at DESC
        """, (user_id,))
    else:
        cursor.execute("""
            SELECT f.file_id, f.user_id, f.file_name, f.file_original,
                   f.file_type, f.file_path, f.file_size, f.shared, f.uploaded_at,
                   u.profilename, u.profession
            FROM uploaded_files f
            JOIN users u ON u.user_id = f.user_id
            WHERE f.user_id=%s
            ORDER BY f.uploaded_at DESC
        """, (user_id,))

    rows = cursor.fetchall()
    cursor.close(); mydb.close()

    files = [{
        'file_id':       r[0],
        'user_id':       r[1],
        'file_name':     r[2],
        'file_original': r[3],
        'file_type':     r[4],
        'file_path':     r[5],
        'file_size':     r[6],
        'shared':        bool(r[7]),
        'uploaded_at':   r[8].strftime("%b %d, %Y") if r[8] else '',
        'uploader':      r[9],
        'profession':    r[10] or 'Student',
        'is_mine':       (r[1] == user_id)
    } for r in rows]

    return jsonify(files)


@notebook_bp.route('/api/toggle-share-file', methods=['POST'])
@login_required
def toggle_share_file():
    """Toggle the shared flag for a file."""
    user_id = session['user_id']
    file_id = request.form.get('file_id')

    mydb   = get_db_connection()
    cursor = mydb.cursor()

    cursor.execute(
        "SELECT shared FROM uploaded_files WHERE file_id=%s AND user_id=%s",
        (file_id, user_id)
    )
    row = cursor.fetchone()
    if not row:
        cursor.close(); mydb.close()
        return jsonify({"success": False, "error": "File not found"})

    new_shared = 0 if row[0] else 1
    cursor.execute(
        "UPDATE uploaded_files SET shared=%s WHERE file_id=%s AND user_id=%s",
        (new_shared, file_id, user_id)
    )
    mydb.commit()
    cursor.close(); mydb.close()

    return jsonify({"success": True, "shared": bool(new_shared)})


@notebook_bp.route('/api/delete-file', methods=['POST'])
@login_required
def delete_file():
    """Delete an uploaded file."""
    user_id = session['user_id']
    file_id = request.form.get('file_id')

    mydb   = get_db_connection()
    cursor = mydb.cursor()

    cursor.execute(
        "SELECT file_path FROM uploaded_files WHERE file_id=%s AND user_id=%s",
        (file_id, user_id)
    )
    row = cursor.fetchone()
    if not row:
        cursor.close(); mydb.close()
        return jsonify({"success": False, "error": "File not found"})

    # Remove from filesystem
    full_path = os.path.join('static', row[0].replace('uploads/', '').lstrip('/'))
    try:
        if os.path.exists(full_path):
            os.remove(full_path)
    except Exception as e:
        print(f"[Notebook] File delete error: {e}")

    cursor.execute(
        "DELETE FROM uploaded_files WHERE file_id=%s AND user_id=%s",
        (file_id, user_id)
    )
    mydb.commit()
    cursor.close(); mydb.close()

    return jsonify({"success": True})


@notebook_bp.route('/view-file/<int:file_id>')
@login_required
def view_file(file_id):
    """Serve file for in-browser preview."""
    user_id = session['user_id']
    mydb    = get_db_connection()
    cursor  = mydb.cursor()

    cursor.execute(
        "SELECT file_path, file_original, file_type, shared, user_id FROM uploaded_files WHERE file_id=%s",
        (file_id,)
    )
    row = cursor.fetchone()
    cursor.close(); mydb.close()

    if not row:
        abort(404)

    # Allow access if owner or shared
    if row[4] != user_id and not row[3]:
        abort(403)

    file_path = row[0]  # e.g. "uploads/1/abc123.pdf"
    parts     = file_path.split('/', 1)
    directory = os.path.join('static', parts[0], str(row[4]))
    filename  = file_path.rsplit('/', 1)[-1]

    return send_from_directory(directory, filename,
                               as_attachment=False,
                               download_name=row[1])
