from bottle import Bottle, template, request, redirect, response, static_file, error
import sqlite3
import hashlib
import os
from werkzeug.utils import secure_filename
import socketio

# Create Bottle instance for HTTP routes
bottle_app = Bottle()
sio = socketio.Server()
SECRET = "supersecretkey"

# --- DB Setup ---
def get_db():
    conn = sqlite3.connect('messenger.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    db = get_db()
    c = db.cursor()

    # Create tables if they don't exist
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL)''')
    c.execute('''CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sender_id INTEGER NOT NULL,
        receiver_id INTEGER,
        group_id INTEGER,
        content TEXT NOT NULL,
        voice_message TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(sender_id) REFERENCES users(id),
        FOREIGN KEY(receiver_id) REFERENCES users(id))''')
    c.execute('''CREATE TABLE IF NOT EXISTS groups (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL)''')
    c.execute('''CREATE TABLE IF NOT EXISTS group_members (
        group_id INTEGER,
        user_id INTEGER,
        FOREIGN KEY(group_id) REFERENCES groups(id),
        FOREIGN KEY(user_id) REFERENCES users(id),
        PRIMARY KEY(group_id, user_id))''')

    # Check and add missing columns to users table
    c.execute("PRAGMA table_info(users)")
    columns = [col[1] for col in c.fetchall()]
    if 'profile_pic' not in columns:
        c.execute("ALTER TABLE users ADD COLUMN profile_pic TEXT")
    if 'theme' not in columns:
        c.execute("ALTER TABLE users ADD COLUMN theme TEXT DEFAULT 'light'")
    if 'is_admin' not in columns:
        c.execute("ALTER TABLE users ADD COLUMN is_admin INTEGER DEFAULT 0")

    db.commit()
    db.close()

# --- Helpers ---
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def get_current_user():
    user_id = request.get_cookie("user_id", secret=SECRET)
    if not user_id:
        return None
    db = get_db()
    c = db.cursor()
    c.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user = c.fetchone()
    db.close()
    return user

def admin_required(func):
    def wrapper(*args, **kwargs):
        user = get_current_user()
        if not user or not user['is_admin']:
            redirect('/login')
        return func(*args, **kwargs)
    return wrapper

# --- Routes ---
@bottle_app.route('/')
def index():
    user = get_current_user()
    if not user:
        return redirect('/login')
    db = get_db()
    c = db.cursor()
    c.execute("SELECT id, username, profile_pic FROM users WHERE id != ?", (user['id'],))
    users = c.fetchall()
    c.execute('''SELECT g.id, g.name FROM groups g JOIN group_members gm ON g.id = gm.group_id WHERE gm.user_id = ?''', (user['id'],))
    groups = c.fetchall()
    db.close()
    return template('index', user=user, users=users, groups=groups)

@bottle_app.route('/register', method=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.forms.get('username').strip()
        password = request.forms.get('password')
        if not username or not password:
            return template('register', error="Введите логин и пароль")
        db = get_db()
        c = db.cursor()
        try:
            c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hash_password(password)))
            db.commit()
        except sqlite3.IntegrityError:
            db.close()
            return template('register', error="Логин занят")
        db.close()
        redirect('/login')
    return template('register', error=None)

@bottle_app.route('/login', method=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.forms.get('username').strip()
        password = request.forms.get('password')
        db = get_db()
        c = db.cursor()
        c.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = c.fetchone()
        db.close()
        if user and hash_password(password) == user['password']:
            response.set_cookie("user_id", str(user['id']), secret=SECRET, path='/')
            redirect('/')
        else:
            return template('login', error="Неверный логин или пароль")
    return template('login', error=None)

@bottle_app.route('/logout')
def logout():
    response.delete_cookie("user_id", path='/')
    redirect('/login')

@bottle_app.route('/settings', method=['GET', 'POST'])
def settings():
    user = get_current_user()
    if not user:
        redirect('/login')
    if request.method == 'POST':
        current_password = request.forms.get('current_password')
        new_username = request.forms.get('username').strip()
        new_password = request.forms.get('new_password')
        profile_pic = request.files.get('profile_pic')
        theme = request.forms.get('theme')
        if not current_password or hash_password(current_password) != user['password']:
            return template('settings', user=user, error="Неверный текущий пароль")
        db = get_db()
        c = db.cursor()
        if new_username and new_username != user['username']:
            try:
                c.execute("UPDATE users SET username = ? WHERE id = ?", (new_username, user['id']))
                db.commit()
            except sqlite3.IntegrityError:
                db.close()
                return template('settings', user=user, error="Логин занят")
        if new_password:
            c.execute("UPDATE users SET password = ? WHERE id = ?", (hash_password(new_password), user['id']))
            db.commit()
        if profile_pic:
            filename = secure_filename(profile_pic.filename)
            filepath = os.path.join('static/uploads', filename)
            profile_pic.save(filepath)
            c.execute("UPDATE users SET profile_pic = ? WHERE id = ?", (filepath, user['id']))
            db.commit()
        if theme:
            c.execute("UPDATE users SET theme = ? WHERE id = ?", (theme, user['id']))
            db.commit()
        db.close()
        redirect('/settings')
    return template('settings', user=user, error=None)

@bottle_app.route('/chat/<peer_id:int>', method=['GET', 'POST'])
def chat(peer_id):
    user = get_current_user()
    if not user:
        redirect('/login')
    if user['id'] == peer_id:
        return "Нельзя чатиться с самим собой!"
    db = get_db()
    c = db.cursor()
    c.execute("SELECT * FROM users WHERE id = ?", (peer_id,))
    peer = c.fetchone()
    if not peer:
        db.close()
        return "Пользователь не найден"
    if request.method == 'POST':
        content = request.forms.get('content').strip()
        file = request.files.get('file')
        if file:
            filename = secure_filename(file.filename)
            filepath = os.path.join('static/uploads', filename)
            file.save(filepath)
            content = f"[Файл: {filename}]"
        if content:
            c.execute("INSERT INTO messages (sender_id, receiver_id, content) VALUES (?, ?, ?)", (user['id'], peer_id, content))
            db.commit()
    c.execute('''SELECT * FROM messages WHERE (sender_id = ? AND receiver_id = ?) OR (sender_id = ? AND receiver_id = ?) ORDER BY timestamp ASC''',
              (user['id'], peer_id, peer_id, user['id']))
    messages = c.fetchall()
    db.close()
    return template('chat', user=user, peer=peer, messages=messages)

@bottle_app.route('/upload_voice', method='POST')
def upload_voice():
    user = get_current_user()
    if not user:
        return {'success': False}
    voice_message = request.files.get('voice_message')
    peer_id = request.forms.get('peer_id')
    if voice_message and peer_id:
        filename = secure_filename(voice_message.filename)
        filepath = os.path.join('static/uploads', filename)
        voice_message.save(filepath)
        db = get_db()
        c = db.cursor()
        c.execute("INSERT INTO messages (sender_id, receiver_id, content, voice_message) VALUES (?, ?, ?, ?)",
                  (user['id'], peer_id, "[Голосовое сообщение]", filepath))
        db.commit()
        db.close()
        return {'success': True}
    return {'success': False}

@bottle_app.route('/create_group', method=['GET', 'POST'])
def create_group():
    user = get_current_user()
    if not user:
        redirect('/login')
    if request.method == 'POST':
        group_name = request.forms.get('group_name').strip()
        if group_name:
            db = get_db()
            c = db.cursor()
            c.execute("INSERT INTO groups (name) VALUES (?)", (group_name,))
            group_id = c.lastrowid
            c.execute("INSERT INTO group_members (group_id, user_id) VALUES (?, ?)", (group_id, user['id']))
            db.commit()
            db.close()
            redirect('/')
    return template('create_group', user=user)

@bottle_app.route('/group/<group_id:int>', method=['GET', 'POST'])
def group(group_id):
    user = get_current_user()
    if not user:
        redirect('/login')
    db = get_db()
    c = db.cursor()
    c.execute("SELECT * FROM groups WHERE id = ?", (group_id,))
    group = c.fetchone()
    if not group:
        db.close()
        return "Группа не найдена"
    c.execute("SELECT * FROM group_members WHERE group_id = ? AND user_id = ?", (group_id, user['id']))
    if not c.fetchone():
        db.close()
        return "Вы не являетесь участником этой группы"
    if request.method == 'POST':
        member_username = request.forms.get('member_username').strip()
        c.execute("SELECT id FROM users WHERE username = ?", (member_username,))
        member = c.fetchone()
        if member:
            c.execute("INSERT OR IGNORE INTO group_members (group_id, user_id) VALUES (?, ?)", (group_id, member['id']))
            db.commit()
    c.execute("SELECT u.id, u.username FROM users u JOIN group_members gm ON u.id = gm.user_id WHERE gm.group_id = ?", (group_id,))
    members = c.fetchall()
    db.close()
    return template('group', user=user, group=group, members=members)

@bottle_app.route('/chat/group/<group_id:int>', method=['GET', 'POST'])
def chat_group(group_id):
    user = get_current_user()
    if not user:
        redirect('/login')
    db = get_db()
    c = db.cursor()
    c.execute("SELECT * FROM groups WHERE id = ?", (group_id,))
    group = c.fetchone()
    if not group:
        db.close()
        return "Группа не найдена"
    c.execute("SELECT * FROM group_members WHERE group_id = ? AND user_id = ?", (group_id, user['id']))
    if not c.fetchone():
        db.close()
        return "Вы не являетесь участником этой группы"
    if request.method == 'POST':
        content = request.forms.get('content').strip()
        if content:
            c.execute("INSERT INTO messages (sender_id, group_id, content) VALUES (?, ?, ?)", (user['id'], group_id, content))
            db.commit()
    c.execute('''SELECT m.*, u.username FROM messages m JOIN users u ON m.sender_id = u.id WHERE m.group_id = ? ORDER BY m.timestamp ASC''', (group_id,))
    messages = c.fetchall()
    db.close()
    return template('chat_group', user=user, group=group, messages=messages)

@bottle_app.route('/admin/users')
@admin_required
def admin_users():
    db = get_db()
    c = db.cursor()
    c.execute("SELECT * FROM users")
    users = c.fetchall()
    db.close()
    user = get_current_user()
    return template('admin_users', user=user, users=users)

@bottle_app.route('/static/<filename:path>')
def serve_static(filename):
    return static_file(filename, root='./static')

# --- Socket.IO Events ---
@sio.event
def connect(sid, environ):
    print('Client connected')

@sio.event
def disconnect(sid):
    print('Client disconnected')

@sio.event
def join_room(sid, data):
    sio.enter_room(sid, data['room'])

@sio.event
def send_message(sid, data):
    room = data['room']
    message = data['message']
    sender_id = data['sender_id']
    db = get_db()
    c = db.cursor()
    if 'receiver_id' in data:
        c.execute("INSERT INTO messages (sender_id, receiver_id, content) VALUES (?, ?, ?)", (sender_id, data['receiver_id'], message))
    elif 'group_id' in data:
        c.execute("INSERT INTO messages (sender_id, group_id, content) VALUES (?, ?, ?)", (sender_id, data['group_id'], message))
    db.commit()
    db.close()
    sio.emit('receive_message', {'message': message, 'sender_id': sender_id}, room=room)

# --- Initialize ---
init_db()
os.makedirs('static/uploads', exist_ok=True)

# Wrap Bottle app with Socket.IO
app = socketio.WSGIApp(sio, bottle_app)

# For WSGI deployment
application = app

# For local run
if __name__ == '__main__':
    from gevent import pywsgi
    from geventwebsocket.handler import WebSocketHandler
    server = pywsgi.WSGIServer(('0.0.0.0', 8080), app, handler_class=WebSocketHandler)
    server.serve_forever()