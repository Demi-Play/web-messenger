# app/socketio.py

from flask_socketio import join_room, leave_room
from . import socketio

@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

@socketio.on('join_chat')
def handle_join_chat(data):
    room = data['chat_id']
    join_room(room)
    print(f'Client joined chat room {room}')
    socketio.emit('user_joined', {'chat_id': room}, room=room)

@socketio.on('leave_chat')
def handle_leave_chat(data):
    room = data['chat_id']
    leave_room(room)
    print(f'Client left chat room {room}')
    socketio.emit('user_left', {'chat_id': room}, room=room)

@socketio.on('send_message')
def handle_send_message(data):
    room = data['chat_id']
    print(f'Message to chat room {room}: {data["message"]}')
    socketio.emit('new_message', data, room=room)

@socketio.on('start_call')
def handle_start_call(data):
    room = data['chat_id']
    print(f'Starting call in chat room {room}')
    socketio.emit('call_started', data, room=room)

@socketio.on('end_call')
def handle_end_call(data):
    room = data['chat_id']
    print(f'Ending call in chat room {room}')
    socketio.emit('call_ended', data, room=room)
