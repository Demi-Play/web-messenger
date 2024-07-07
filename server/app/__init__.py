# app/__init__.py

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO
from flask_jwt_extended import JWTManager

db = SQLAlchemy()
socketio = SocketIO()
jwt = JWTManager()


def create_app():
    app = Flask(__name__)
    app.config.from_object('app.config.Config')
    db.init_app(app)

    with app.app_context():
        from app.models import User, Chat, Message, ChatParticipant
        # Create all tables
        db.create_all()
    
    socketio.init_app(app)
    jwt.init_app(app)
    

    from app.routes import main_bp
    app.register_blueprint(main_bp)

    return app
