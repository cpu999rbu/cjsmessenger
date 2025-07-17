from db import get_db
import bcrypt

def hash_password(pw: str):
    return bcrypt.hashpw(pw.encode('utf-8'), bcrypt.gensalt())

def check_password(pw: str, pw_hash: bytes):
    return bcrypt.checkpw(pw.encode('utf-8'), pw_hash)

def register_user(username, password):
    db = get_db()
    pw_hash = hash_password(password)
    try:
        db.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", (username, pw_hash))
        db.commit()
        return True
    except db.IntegrityError:
        return False

def login_user(username, password):
    db = get_db()
    row = db.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
    if row and check_password(password, row['password_hash']):
        return row['id']
    return None

def get_current_user(session):
    user_id = session.get('user')
    if user_id:
        db = get_db()
        return db.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    return None