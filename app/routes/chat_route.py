from datetime import timedelta

from flask import Blueprint, render_template
from flask_login import current_user, login_required

from app.model.user import User

chat_bp = Blueprint('chat', __name__)

@chat_bp.route('/')
@login_required
def index():
    users = User.query.filter(User.id != current_user.id).all()
    return render_template('chat.html', users=users, current_user=current_user)

from flask import jsonify
from flask_login import current_user, login_required

from app.model.message import Message


@chat_bp.route('/get_messages/<int:user_id>')
@login_required
def get_messages(user_id):
    msgs = Message.query.filter(
        ((Message.sender_id == current_user.id) & (Message.receiver_id == user_id)) |
        ((Message.sender_id == user_id) & (Message.receiver_id == current_user.id))
    ).order_by(Message.timestamp).all()
    # --- TIME ADD KIYA ---
    return jsonify([{'message': m.content, 'sender_id': m.sender_id, 'time': (m.timestamp + timedelta(hours=5, minutes=30)).strftime("%I:%M %p")} for m in msgs])