from bottle import Bottle, run, template, request, redirect, static_file
from bottle_sessions import SessionsPlugin
from db import init_db, get_db
import auth, json
from gevent import pywsgi
from geventwebsocket.handler import WebSocketHandler

app = Bottle()
app.install(SessionsPlugin(secret="SECRET_KEY", cookie_lifetime=86400, path="/", httponly=True))
init_db()

connected = {}

def broadcast(msg):
    for ws in list(connected.values()):
        try:
            ws.send(json.dumps(msg))
        except:
            pass

@app.route('/static/<filepath:path>')
def static(filepath):
    return static_file(filepath, root='./static')

@app.get('/')
def home(session):
    user = auth.get_current_user(session)
    if not user:
        redirect('/login')
    db = get_db()
    users = db.execute("SELECT * FROM users").fetchall()
    return template('home', user=user, users=users)

@app.get('/login')
def login_form():
    return template('login')

@app.post('/login')
def do_login(session):
    u = request.forms.get('username')
    p = request.forms.get('password')
    user_id = auth.login_user(u, p)
    if user_id:
        session['user'] = user_id
        redirect('/')
    return template('login', error="Неверные данные")

@app.get('/register')
def register_form():
    return template('register')

@app.post('/register')
def do_register():
    u = request.forms.get('username')
    p = request.forms.get('password')
    if auth.register_user(u, p):
        redirect('/login')
    return template('register', error="Пользователь уже существует")

@app.get('/chat/<recipient_id:int>')
def chat(session, recipient_id):
    user = auth.get_current_user(session)
    if not user:
        redirect('/login')
    db = get_db()
    recipient = db.execute("SELECT * FROM users WHERE id = ?", (recipient_id,)).fetchone()
    messages = db.execute("SELECT * FROM messages WHERE chat_id=? ORDER BY timestamp", (recipient_id,)).fetchall()
    return template('chat', user=user, recipient=recipient, messages=messages)

@app.post('/chat/<recipient_id:int>')
def send_message(session, recipient_id):
    user = auth.get_current_user(session)
    if not user:
        redirect('/login')
    content = request.forms.get('message')
    db = get_db()
    if content.strip():
        db.execute("INSERT INTO messages (chat_id, user_id, content) VALUES (?, ?, ?)",
                   (recipient_id, user['id'], content))
        db.commit()
        # broadcast new message
        if recipient_id in connected:
            connected[recipient_id].send(json.dumps({
                'type':'message', 'from': user['id'], 'text': content
            }))
    redirect(f'/chat/{recipient_id}')

@app.post('/upload_voice')
def upload_voice(session):
    user = auth.get_current_user(session)
    if not user:
        redirect('/login')
    voice = request.files.get('voice')
    if voice:
        save_path = f"static/media/{user['id']}_voice_{voice.filename}"
        voice.save(save_path)
        db = get_db()
        db.execute("INSERT INTO messages (chat_id, user_id, content) VALUES (?, ?, ?)",
                   (user['id'], user['id'], f"[voice]{save_path}"))
        db.commit()
    redirect('/')

@app.post('/upload_video')
def upload_video(session):
    user = auth.get_current_user(session)
    if not user:
        redirect('/login')
    video = request.files.get('video')
    if video:
        save_path = f"static/media/{user['id']}_video_{video.filename}"
        video.save(save_path)
        db = get_db()
        db.execute("INSERT INTO messages (chat_id, user_id, content) VALUES (?, ?, ?)",
                   (user['id'], user['id'], f"[video]{save_path}"))
        db.commit()
    redirect('/')

# Settings, search, create_group routes omitted for brevity; assume as before

@app.route('/ws')
def handle_ws(ws):
    session = request.environ.get('beaker.session') or {}  # adjust if using bottle-sessions
    user = auth.get_current_user(session)
    if not user or not ws:
        return
    connected[user['id']] = ws
    broadcast({'type':'status','user_id':user['id'],'online':True})
    try:
        while True:
            data = ws.receive()
            if data is None:
                break
            msg = json.loads(data)
            if msg['type']=='typing':
                to = msg['to']
                if to in connected:
                    connected[to].send(json.dumps({'type':'typing','user_id':user['id'],'user_name':user['username'],'typing':True}))
            elif msg['type']=='status':
                pass
    finally:
        connected.pop(user['id'],None)
        broadcast({'type':'status','user_id':user['id'],'online':False})

if __name__ == '__main__':
    server = pywsgi.WSGIServer(('',8080), app, handler_class=WebSocketHandler)
    server.serve_forever()