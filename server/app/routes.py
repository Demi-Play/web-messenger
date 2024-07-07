# app/routes.py

from flask import Blueprint, request, jsonify, make_response
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from .models import db, User, Chat, Message, ChatParticipant
from .socketio import socketio

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return "Welcome to the Messenger API!"

# Регистрация пользователя
@main_bp.route('/register', methods=['POST'])
def register_user():
    data = request.get_json()
    new_user = User(username=data['username'], email=data['email'])
    new_user.set_password(data['password'])
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "User registered successfully!"}), 201

# Аутентификация пользователя
@main_bp.route('/login', methods=['POST'])
def login_user():
    data = request.get_json()
    user = User.query.filter_by(username=data['username']).first()
    if user and user.check_password(data['password']):
        access_token = create_access_token(identity={'username': user.username, 'email': user.email})
        return jsonify(access_token=access_token), 200
    else:
        return jsonify({"message": "Invalid credentials"}), 401
    
# Создание чата
@main_bp.route('/chats', methods=['POST'])
@jwt_required()
def create_chat():
    data = request.get_json()
    current_user_id = get_jwt_identity()
    new_chat = Chat(name=data['name'], type=data['type'])
    db.session.add(new_chat)
    db.session.commit()
    # Добавляем текущего пользователя как участника чата
    participant = ChatParticipant(chat_id=new_chat.id, user_id=current_user_id)
    db.session.add(participant)
    db.session.commit()
    return jsonify({"message": "Chat created successfully!", "chat_id": new_chat.id}), 201

# Отправка сообщения
@main_bp.route('/messages', methods=['POST'])
@jwt_required()
def send_message():
    data = request.get_json()
    current_user_id = get_jwt_identity()
    new_message = Message(chat_id=data['chat_id'], sender_id=current_user_id, content=data['content'])
    db.session.add(new_message)
    db.session.commit()
    # Отправляем сообщение через WebSocket всем участникам чата
    socketio.emit('new_message', {'chat_id': data['chat_id'], 'message': data['content']}, broadcast=True)
    return jsonify({"message": "Message sent successfully!"}), 201

# Получение всех чатов пользователя
@main_bp.route('/chats', methods=['GET'])
@jwt_required()
def get_chats():
    current_user_id = get_jwt_identity()
    chats = Chat.query.join(ChatParticipant).filter(ChatParticipant.user_id == current_user_id).all()
    return jsonify([chat.name for chat in chats]), 200
