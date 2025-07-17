from flask import Flask, render_template, request, redirect, url_for, Response, session, send_from_directory
from flask_socketio import SocketIO, join_room, emit
import sqlite3
import hashlib
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SECRET_KEY'] = 'supersecretkey'
socketio = SocketIO(app)

UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# --- DB Setup ---
def get_db():
    conn = sqlite3.connect('messenger.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    db = get_db()
    c = db.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        profile_pic TEXT,
        theme TEXT DEFAULT 'light',
        is_admin INTEGER DEFAULT 0)''')
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
    db.commit()
    db.close()

# --- Helpers ---
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def get_current_user():
    user_id = session.get('user_id')
    if not user_id:
        return None
    db = get_db()
    c = db.cursor()
    c.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user = c.fetchone()
    db.close()
    return user

def admin_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = get_current_user()
        if not user or not user['is_admin']:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# --- Routes ---
@app.route('/')
def index():
    user = get_current_user()
    if not user:
        return redirect(url_for('login'))
    db = get_db()
    c = db.cursor()
    c.execute("SELECT id, username, profile_pic FROM users WHERE id != ?", (user['id'],))
    users = c.fetchall()
    c.execute('''SELECT g.id, g.name FROM groups g JOIN group_members gm ON g.id = gm.group_id WHERE gm.user_id = ?''', (user['id'],))
    groups = c.fetchall()
    db.close()
    return render_template('index.html', user=user, users=users, groups=groups)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username').strip()
        password = request.form.get('password')
        if not username or not password:
            return render_template('register.html', error="Введите логин и пароль")
        db = get_db()
        c = db.cursor()
        try:
            c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hash_password(password)))
            db.commit()
        except sqlite3.IntegrityError:
            db.close()
            return render_template('register.html', error="Логин занят")
        db.close()
        return redirect(url_for('login'))
    return render_template('register.html', error=None)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username').strip()
        password = request.form.get('password')
        db = get_db()
        c = db.cursor()
        c.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = c.fetchone()
        db.close()
        if user and hash_password(password) == user['password']:
            session['user_id'] = user['id']
            return redirect(url_for('index'))
        return render_template('login.html', error="Неверный логин или пароль")
    return render_template('login.html', error=None)

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))

@app.route('/settings', methods=['GET', 'POST'])
def settings():
    user = get_current_user()
    if not user:
        return redirect(url_for('login'))
    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_username = request.form.get('username').strip()
        new_password = request.form.get('new_password')
        profile_pic = request.files.get('profile_pic')
        theme = request.form.get('theme')
        if not current_password or hash_password(current_password) != user['password']:
            return render_template('settings.html', user=user, error="Неверный текущий пароль")
        db = get_db()
        c = db.cursor()
        if new_username and new_username != user['username']:
            try:
                c.execute("UPDATE users SET username = ? WHERE id = ?", (new_username, user['id']))
                db.commit()
            except sqlite3.IntegrityError:
                db.close()
                return render_template('settings.html', user=user, error="Логин занят")
        if new_password:
            c.execute("UPDATE users SET password = ? WHERE id = ?", (hash_password(new_password), user['id']))
            db.commit()
        if profile_pic:
            filename = secure_filename(profile_pic.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            profile_pic.save(filepath)
            c.execute("UPDATE users SET profile_pic = ? WHERE id = ?", (filepath, user['id']))
            db.commit()
        if theme:
            c.execute("UPDATE users SET theme = ? WHERE id = ?", (theme, user['id']))
            db.commit()
        db.close()
        return redirect(url_for('settings'))
    return render_template('settings.html', user=user, error=None)

@app.route('/chat/<int:peer_id>', methods=['GET', 'POST'])
def chat(peer_id):
    user = get_current_user()
    if not user:
        return redirect(url_for('login'))
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
        content = request.form.get('content').strip()
        file = request.files.get('file')
        if file:
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            content = f"[Файл: {filename}]"
        if content:
            c.execute("INSERT INTO messages (sender_id, receiver_id, content) VALUES (?, ?, ?)", (user['id'], peer_id, content))
            db.commit()
    c.execute('''SELECT * FROM messages WHERE (sender_id = ? AND receiver_id = ?) OR (sender_id = ? AND receiver_id = ?) ORDER BY timestamp ASC''',
              (user['id'], peer_id, peer_id, user['id']))
    messages = c.fetchall()
    db.close()
    return render_template('chat.html', user=user, peer=peer, messages=messages, chat_id=f"{min(user['id'], peer_id)}_{max(user['id'], peer_id)}")

@app.route('/upload_voice', methods=['POST'])
def upload_voice():
    user = get_current_user()
    if not user:
        return {'success': False}
    voice_message = request.files.get('voice_message')
    peer_id = request.form.get('peer_id')
    if voice_message and peer_id:
        filename = secure_filename(voice_message.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        voice_message.save(filepath)
        db = get_db()
        c = db.cursor()
        c.execute("INSERT INTO messages (sender_id, receiver_id, content, voice_message) VALUES (?, ?, ?, ?)",
                  (user['id'], peer_id, "[Голосовое сообщение]", filepath))
        db.commit()
        db.close()
        return {'success': True}
    return {'success': False}

@app.route('/create_group', methods=['GET', 'POST'])
def create_group():
    user = get_current_user()
    if not user:
        return redirect(url_for('login'))
    if request.method == 'POST':
        group_name = request.form.get('group_name').strip()
        if group_name:
            db = get_db()
            c = db.cursor()
            c.execute("INSERT INTO groups (name) VALUES (?)", (group_name,))
            group_id = c.lastrowid
            c.execute("INSERT INTO group_members (group_id, user_id) VALUES (?, ?)", (group_id, user['id']))
            db.commit()
            db.close()
            return redirect(url_for('index'))
    return render_template('create_group.html', user=user)

@app.route('/group/<int:group_id>', methods=['GET', 'POST'])
def group(group_id):
    user = get_current_user()
    if not user:
        return redirect(url_for('login'))
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
        member_username = request.form.get('member_username').strip()
        c.execute("SELECT id FROM users WHERE username = ?", (member_username,))
        member = c.fetchone()
        if member:
            c.execute("INSERT OR IGNORE INTO group_members (group_id, user_id) VALUES (?, ?)", (group_id, member['id']))
            db.commit()
    c.execute("SELECT u.id, u.username FROM users u JOIN group_members gm ON u.id = gm.user_id WHERE gm.group_id = ?", (group_id,))
    members = c.fetchall()
    db.close()
    return render_template('group.html', user=user, group=group, members=members)

@app.route('/chat/group/<int:group_id>', methods=['GET', 'POST'])
def chat_group(group_id):
    user = get_current_user()
    if not user:
        return redirect(url_for('login'))
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
        content = request.form.get('content').strip()
        if content:
            c.execute("INSERT INTO messages (sender_id, group_id, content) VALUES (?, ?, ?)", (user['id'], group_id, content))
            db.commit()
    c.execute('''SELECT m.*, u.username FROM messages m JOIN users u ON m.sender_id = u.id WHERE m.group_id = ? ORDER BY m.timestamp ASC''', (group_id,))
    messages = c.fetchall()
    db.close()
    return render_template('chat_group.html', user=user, group=group, messages=messages, chat_id=f"group_{group_id}")

@app.route('/admin/users')
@admin_required
def admin_users():
    db = get_db()
    c = db.cursor()
    c.execute("SELECT * FROM users")
    users = c.fetchall()
    db.close()
    user = get_current_user()
    return render_template('admin_users.html', user=user, users=users)

@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)

# --- Socket.IO Events ---
@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

@socketio.on('join_room')
def handle_join_room(data):
    join_room(data['room'])

@socketio.on('send_message')
def handle_send_message(data):
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
    emit('receive_message', {'message': message, 'sender_id': sender_id}, room=room)

# --- Initialize ---
init_db()
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=8080)
