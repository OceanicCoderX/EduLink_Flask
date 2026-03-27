# EduLink — Flask Version 🎓

> A smart student productivity web app with live chat, video study rooms, and a social community.

---

## 📁 Project Structure

```
Edulink_Flask/
├── app.py                  ← Main Flask app (start this!)
├── config.py               ← Database & secret key config
├── db.py                   ← get_db_connection() helper
├── socket_events.py        ← All SocketIO event handlers
├── requirements.txt        ← Python packages list
├── edulink_updated.sql     ← Updated database schema (import this)
│
├── routes/                 ← One file per feature (Flask Blueprints)
│   ├── auth.py             ← Login, Signup, Logout, Forgot Password
│   ├── dashboard.py        ← Dashboard + stats API
│   ├── tasks.py            ← Tasks CRUD
│   ├── focus.py            ← Focus timer + save session
│   ├── notebook.py         ← Notes CRUD (linked to user)
│   ├── classroom.py        ← Study rooms + room page
│   ├── community.py        ← Posts feed + groups + follow
│   ├── profile.py          ← Profile view + edit
│   └── friends.py          ← Friends Stack page
│
├── templates/              ← HTML files (Jinja2 templates)
│   ├── base.html           ← Common layout (sidebar, nav)
│   ├── login.html
│   ├── signup.html
│   └── pages/
│       ├── dashboard.html
│       ├── tasks.html
│       ├── focus.html
│       ├── notebook.html
│       ├── classroom.html
│       ├── room.html       ← Study room (chat + video)
│       ├── community.html
│       ├── friends_stack.html
│       └── profile.html
│
└── static/                 ← CSS, JS, Images (was "assets/" in CGI version)
    ├── css/
    ├── js/
    └── images/
        ├── users/          ← Profile pictures (per user_id folder)
        └── background/     ← Cover pictures (per user_id folder)
```

---

## ⚙️ Flask Architecture

### How it works (instead of CGI)

**Old way (CGI):** Every `.py` file was a separate script. Apache ran each file like a program when someone visited the URL. Each file printed raw HTML with `print("""...""")`.

**New way (Flask):** One app (`app.py`) runs continuously. Routes are registered using `@app.route('/path')`. Templates (`.html` files) are returned using `render_template()`.

### Blueprints

Every feature is split into its own "Blueprint" file in the `routes/` folder. This keeps code organized. In `app.py`, all blueprints are registered:

```python
app.register_blueprint(auth_bp)
app.register_blueprint(tasks_bp)
# etc.
```

### Session (Login)

After login, Flask stores the user's info in an encrypted cookie using `session`:

```python
session['user_id']     = user_row[0]
session['profilename'] = user_row[3]
session['email']       = user_row[6]
```

Every page checks `if 'user_id' not in session: redirect to login`. This replaces the old `user_id = 1  # static` lines.

---

## 🗄️ Database Connection

**File:** `db.py`

```python
import mysql.connector
from config import DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME

def get_db_connection():
    mydb = mysql.connector.connect(
        host=DB_HOST,          # localhost
        port=DB_PORT,          # 3306
        user=DB_USER,          # root
        password=DB_PASSWORD,  # "" (XAMPP default)
        database=DB_NAME,      # edulink
        ssl_disabled=True,
        use_pure=True
    )
    return mydb
```

**How to use it in any route:**

```python
mydb   = get_db_connection()
cursor = mydb.cursor()
cursor.execute("SELECT * FROM users WHERE user_id=%s", (user_id,))
result = cursor.fetchone()
cursor.close()
mydb.close()
```

**Important:** Always use `%s` placeholders (parameterized queries). Never use f-strings or string formatting for SQL — that causes SQL injection.

---

## 📊 Database Changes (from original)

| Table | What changed |
|---|---|
| `notes` | Added `user_id`, `category`, `tags` columns |
| `users` | `password` column size increased from `varchar(10)` to `varchar(255)` |
| `classroom` | Added `subject` column |
| `room_members` | Added `UNIQUE` constraint on `(member_id, room_id)` |
| `classroom_messages` | **NEW** — stores room chat messages |
| `posts` | **NEW** — community feed posts |
| `post_likes` | **NEW** — likes on posts |
| `post_comments` | **NEW** — comments on posts |
| `community_messages` | **NEW** — per-subject live chat messages |
| `follows` | **NEW** — friend/follow system |

---

## 💬 How Real-time Chat Works (Flask-SocketIO)

### The Technology

SocketIO creates a **persistent connection** between browser and server. Unlike normal HTTP (where browser asks, server answers, connection closes), SocketIO keeps the connection open so the server can send messages to the browser at any time.

### Flow (Classroom Chat)

```
1. User opens /room/5
2. Browser connects to SocketIO server
3. Browser emits: socket.emit('join_classroom_room', {room_id: 5})
4. Server: join_room('classroom_5')  ← now this user is in that "room group"
5. User types message, clicks send
6. Browser emits: socket.emit('classroom_send_message', {room_id: 5, message: "hello"})
7. Server saves to DB, then:
8. Server: emit('classroom_new_message', data, to='classroom_5')
9. All browsers in 'classroom_5' receive the message instantly
10. JavaScript appends new message to chat box
```

### File: `socket_events.py`

All SocketIO event handlers are in this one file. There are two groups:
- **Classroom events:** `join_classroom_room`, `classroom_send_message`, WebRTC signaling
- **Community events:** `join_community_room`, `community_send_message`

### Community Chat Rooms

Each subject in each group is a separate "room key":

```python
room_key = f"community_{group_id}_{subject}"
# Example: "community_3_physics"
```

Only members of that community group can join. Admin controls who is a member.

---

## 📹 How Video Chat Works (WebRTC Mesh)

### The Technology

WebRTC is a browser API that lets browsers connect directly to each other (peer-to-peer). No video goes through your server — it goes directly between users. This is called "mesh" topology.

Works best for 2–4 people. For larger groups, a media server (like mediasoup) would be needed — but we chose mesh for simplicity.

### Flow

```
User A opens /room/5 and clicks "Cam On"
  → Gets camera stream from browser
  → Emits: webrtc_user_ready

Server receives webrtc_user_ready
  → Emits: webrtc_new_peer to everyone else in the room

User B receives webrtc_new_peer
  → Creates RTCPeerConnection to User A
  → Creates an "offer" (SDP description of what it can do)
  → Sends offer via: socket.emit('webrtc_offer', {target_sid: A's socket ID, offer})

Server forwards offer to User A

User A receives offer
  → Creates RTCPeerConnection to User B
  → Creates an "answer"
  → Sends answer via: socket.emit('webrtc_answer', {target_sid: B's socket ID, answer})

Both sides exchange ICE candidates (network path info)
  → socket.emit('webrtc_ice_candidate', {target_sid, candidate})

Connection established — video flows directly peer-to-peer
```

### Key Points

- `request.sid` = each socket connection's unique ID — used to route WebRTC messages
- ICE candidates tell WebRTC how to find the other peer on the network
- STUN servers (`stun.l.google.com`) help find public IP addresses on different networks
- On the same local network (same WiFi/LAN), it works without STUN

---

## 🚀 How to Run the Project on XAMPP

### Step 1: Setup XAMPP

1. Open XAMPP Control Panel
2. Start **Apache** and **MySQL**
3. Open **phpMyAdmin**: `http://localhost/phpmyadmin`

### Step 2: Import Database

1. In phpMyAdmin, click "New" to create database `edulink`
2. Select the `edulink` database
3. Click "Import"
4. Choose `edulink_updated.sql`
5. Click "Go"

### Step 3: Install Python Packages

Open terminal/command prompt in the `Edulink_Flask/` folder:

```bash
pip install -r requirements.txt
```

### Step 4: Check Config

Open `config.py`:

```python
DB_HOST     = "localhost"
DB_PORT     = 3306
DB_USER     = "root"
DB_PASSWORD = ""          # XAMPP default — no password
DB_NAME     = "edulink"
```

Change `DB_PASSWORD` if your XAMPP MySQL has a password set.

### Step 5: Run

```bash
python app.py
```

Open browser: **http://127.0.0.1:5000**

Login with:
- Email: `khushishewale797@gmail.com`
- Password: `Khushi@123`

---

## 📦 Required Packages

```
Flask==3.0.3                  ← Web framework
flask-socketio==5.3.6         ← Real-time WebSocket support
mysql-connector-python==8.3.0 ← MySQL database driver
eventlet==0.36.1              ← Async server (required by SocketIO)
```

Install all at once: `pip install -r requirements.txt`

---

## 🔐 Plain Text Password → bcrypt (Future Upgrade)

Currently passwords are stored as plain text (as requested). Here's how to upgrade to bcrypt later:

**Step 1: Install bcrypt**
```bash
pip install bcrypt
```

**Step 2: In `routes/auth.py`, change signup:**
```python
import bcrypt

# When saving password (signup):
hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
# Save `hashed` instead of `password`
```

**Step 3: In `routes/auth.py`, change login:**
```python
# When checking password (login):
# result[7] is the stored hash from DB
if result and bcrypt.checkpw(password.encode('utf-8'), result[7].encode('utf-8')):
    set_user_session(result)
    return redirect(url_for('dashboard.dashboard'))
```

**Step 4: Update existing passwords in DB:**
Run this once to hash all existing plain text passwords:
```python
import bcrypt, mysql.connector
db = mysql.connector.connect(host='localhost', user='root', password='', database='edulink')
cur = db.cursor()
cur.execute("SELECT user_id, password FROM users")
for row in cur.fetchall():
    hashed = bcrypt.hashpw(row[1].encode(), bcrypt.gensalt()).decode()
    cur.execute("UPDATE users SET password=%s WHERE user_id=%s", (hashed, row[0]))
db.commit()
print("Done")
```

---

## 🐛 Common Errors & Fixes

### Error: `mysql.connector.errors.InterfaceError: 2003: Can't connect to MySQL server`
**Fix:** XAMPP MySQL is not running. Open XAMPP Control Panel → Start MySQL.

### Error: `ModuleNotFoundError: No module named 'flask_socketio'`
**Fix:** Run `pip install flask-socketio eventlet`

### Error: `jinja2.exceptions.UndefinedError: 'enumerate' is undefined`
**Fix:** The `community.html` uses `enumerate` in a Jinja2 loop. Use `loop.index` instead:
```html
{% for person in leaderboard %}
<div class="rank">{{ loop.index }}</div>
```
(Already fixed in the template — use `loop.index`)

### Error: `Access denied for user 'root'@'localhost'`
**Fix:** Your XAMPP MySQL has a password. Set it in `config.py`:
```python
DB_PASSWORD = "your_password_here"
```

### Error: `SocketIO chat not working`
**Fix:** Make sure you have `eventlet` installed: `pip install eventlet`. Also check that `async_mode='threading'` is set in `app.py`.

### Error: `WebRTC video not working on different networks`
**Fix:** WebRTC mesh works best on the same network. For different networks, STUN servers are used (already included). If still not working, it may be due to a strict firewall/NAT. This is a known limitation of the mesh approach.

### Error: `500 Internal Server Error` on community page
**Fix:** The `enumerate` Jinja2 filter issue. In `community.html`, change:
```html
{% for i, person in leaderboard | enumerate %}
```
to:
```html
{% for person in leaderboard %}
```
And use `{{ loop.index }}` for rank numbers. (Already fixed in the provided code.)

### Port 5000 already in use
**Fix:** Change port in `app.py`:
```python
socketio.run(app, debug=True, host="127.0.0.1", port=5001)
```
Then access at `http://127.0.0.1:5001`

---

## 🗺️ URL Routes Reference

| URL | Method | What it does |
|---|---|---|
| `/` | GET | Landing page |
| `/login` | GET/POST | Login page + form |
| `/signup` | GET/POST | Signup page + form |
| `/logout` | GET | Clear session, redirect login |
| `/dashboard` | GET | Dashboard |
| `/tasks` | GET | Tasks page |
| `/focus` | GET | Focus timer |
| `/notebook` | GET | Notebook |
| `/classroom` | GET | Classroom (room list) |
| `/room/<id>` | GET | Study room (chat + video) |
| `/community` | GET | Community feed |
| `/friends-stack` | GET | Friends Stack page |
| `/profile` | GET | Profile page |
| `/api/tasks` | GET | Get user's tasks (JSON) |
| `/api/save-task` | POST | Save new task |
| `/api/save-focus` | POST | Save focus session |
| `/api/notes` | GET | Get user's notes |
| `/api/save-note` | POST | Save new note |
| `/api/create-room` | POST | Create study room |
| `/api/get-posts` | GET | Get community posts |
| `/api/follow` | POST | Follow a user |
| `/api/unfollow` | POST | Unfollow a user |

---

## 🔄 What Changed from CGI to Flask (Summary)

| Old (CGI) | New (Flask) |
|---|---|
| `#!C:/Python310/python.exe` at top of every file | Just `from flask import ...` |
| `print("Content-Type:text/html\n")` | `return render_template('page.html')` |
| `print("""..HTML...""")` | Clean `.html` template files |
| `import cgi` / `form.getvalue()` | `request.form.get()` |
| `user_id = 1  # static` | `user_id = session['user_id']` |
| `window.location.href = "page.py"` | Flask url_for: `url_for('dashboard.dashboard')` |
| DB in every file | `db.py` → `get_db_connection()` used everywhere |
| No real-time features | Flask-SocketIO + WebRTC |
