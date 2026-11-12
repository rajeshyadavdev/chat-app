from datetime import timedelta

from flask import Flask
from flask_login import LoginManager, current_user
from flask_socketio import SocketIO, emit, join_room
from flask_sqlalchemy import SQLAlchemy

from config import Config

db = SQLAlchemy()
login_manager = LoginManager()
socketio = SocketIO()

online_users = {}  # user_id -> kitne tab khule hain

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    login_manager.init_app(app)
    socketio.init_app(app, cors_allowed_origins="*", async_mode='gevent')
    
    login_manager.login_view = 'auth.login'
    
    @login_manager.user_loader
    def load_user(user_id):
        from app.model import User
        return User.query.get(int(user_id))
    
    from app.routes.auth_route import auth_bp
    from app.routes.chat_route import chat_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(chat_bp)
    
    from app import model
    
    with app.app_context():
        db.create_all()

    @socketio.on('join')
    def on_join(data):
        room = data['room']
        join_room(room)
        print(f"User {current_user.username} joined room: {room}")

    @socketio.on('send_message')
    def handle_message(data):
      room = data['room']
      parts = room.replace('room_', '').split('_')
      user1, user2 = int(parts[0]), int(parts[1])
      receiver_id = user2 if current_user.id == user1 else user1

      from app.model import Message
      msg = Message(sender_id=current_user.id, receiver_id=receiver_id, content=data['message'])
      db.session.add(msg)
      db.session.commit()

      # --- 1. TIME ADD KIYA ---
      time_str = (msg.timestamp + timedelta(hours=5, minutes=30)).strftime("%I:%M %p")

      emit('receive_message', {
        'message': data['message'],
        'sender_id': current_user.id,
        'time': time_str  # <-- ye line nayi hai
      }, room=room, include_self=False)

    # --- 2. TYPING HANDLER ADD KIYA ---
    @socketio.on('typing')
    def handle_typing(data):
        emit('user_typing', {
            'username': current_user.username
        }, room=data['room'], include_self=False)
      
    @socketio.on('connect')
    def handle_connect():
        if current_user.is_authenticated:
            online_users[current_user.id] = online_users.get(current_user.id, 0) + 1
            emit('user_status', {'user_id': current_user.id, 'status': 'online'}, broadcast=True)
            emit('online_users_list', {'online_ids': list(online_users.keys())})
            print(f"{current_user.username} ONLINE")

    @socketio.on('disconnect')
    def handle_disconnect():
        if current_user.is_authenticated:
            online_users[current_user.id] = online_users.get(current_user.id, 1) - 1
            if online_users[current_user.id] <= 0:
                del online_users[current_user.id]
                emit('user_status', {'user_id': current_user.id, 'status': 'offline'}, broadcast=True)
                print(f"{current_user.username} OFFLINE")  

    return app, socketio