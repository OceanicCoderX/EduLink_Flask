# ============================================================
# app.py — EduLink Main Flask App
# Updated: MAX_CONTENT_LENGTH for file uploads, Flask-Mail config
# ============================================================

from flask import Flask
from flask_socketio import SocketIO
from config import (SECRET_KEY, MAX_CONTENT_LENGTH,
                    MAIL_SERVER, MAIL_PORT, MAIL_USE_TLS,
                    MAIL_USERNAME, MAIL_PASSWORD, MAIL_DEFAULT_SENDER,
                    UPLOAD_FOLDER)
import os

# --- App Initialize ---
app = Flask(__name__)
app.secret_key = SECRET_KEY

# --- File Upload Config ---
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH
app.config['UPLOAD_FOLDER']      = UPLOAD_FOLDER

# --- Flask-Mail Config ---
app.config['MAIL_SERVER']         = MAIL_SERVER
app.config['MAIL_PORT']           = MAIL_PORT
app.config['MAIL_USE_TLS']        = MAIL_USE_TLS
app.config['MAIL_USERNAME']       = MAIL_USERNAME
app.config['MAIL_PASSWORD']       = MAIL_PASSWORD
app.config['MAIL_DEFAULT_SENDER'] = MAIL_DEFAULT_SENDER

# --- SocketIO Initialize (real-time chat ke liye) ---
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# --- Ensure upload directory exists ---
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# --- Import & Register all route blueprints ---
from routes.auth       import auth_bp
from routes.dashboard  import dashboard_bp
from routes.tasks      import tasks_bp
from routes.focus      import focus_bp
from routes.notebook   import notebook_bp
from routes.profile    import profile_bp
from routes.classroom  import classroom_bp
from routes.community  import community_bp
from routes.friends    import friends_bp

app.register_blueprint(auth_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(tasks_bp)
app.register_blueprint(focus_bp)
app.register_blueprint(notebook_bp)
app.register_blueprint(profile_bp)
app.register_blueprint(classroom_bp)
app.register_blueprint(community_bp)
app.register_blueprint(friends_bp)

# --- SocketIO Events Import (must be after socketio is created) ---
import socket_events   # noqa: F401

# --- Run ---
if __name__ == "__main__":
    print("EduLink running at http://127.0.0.1:5000")
    socketio.run(app, debug=True, host="127.0.0.1", port=5000, allow_unsafe_werkzeug=True)