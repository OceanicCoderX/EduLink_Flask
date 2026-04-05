# ============================================================
# app.py — EduLink Main Flask App
# Yahan sab routes register hote hain aur SocketIO start hota hai
# ============================================================

from flask import Flask
from flask_socketio import SocketIO
from config import SECRET_KEY

# --- App Initialize ---
app = Flask(__name__)
app.secret_key = SECRET_KEY

# --- SocketIO Initialize (real-time chat ke liye) ---
# async_mode='threading' — XAMPP/Windows pe kaam karta hai
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

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
import socket_events   # noqa: F401  — yeh file events handle karti hai

# --- Run ---
if __name__ == "__main__":
    print("EduLink running at http://127.0.0.1:5000")
    socketio.run(app, debug=True, host="127.0.0.1", port=5000, allow_unsafe_werkzeug=True)
