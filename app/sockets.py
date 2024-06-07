from flask import request
from flask_socketio import emit, join_room, leave_room
import time
import app
from app import socketio
from app.models.message_model import Messages
from app.services.conversation_services import create_new_conversation
from app.services.message_services import save_message

online_users = {}

@socketio.on('connect')
def handle_connect():
    user_id = request.args.get('user_id')
    online_users[user_id] = {'status': 'online', 'last_active': time.time()}
    emit('user_status', {'user_id': user_id, 'status': 'online'}, broadcast=True)

@socketio.on('disconnect')
def handle_disconnect():
    user_id = request.args.get('user_id')
    if user_id in online_users:
        online_users[user_id]['status'] = 'offline'
        emit('user_status', {'user_id': user_id, 'status': 'offline'}, broadcast=True)

@socketio.on('check_status')
def check_status(data):
    user_id = data['user_id']
    status = online_users.get(user_id, {'status': 'offline'})
    emit('status_response', {'user_id': user_id, 'status': status['status']})

@socketio.on('get_contact_statuses')
def get_contact_statuses(data):
    contact_ids = data['contact_ids']
    statuses = {user_id: online_users.get(user_id, {'status': 'offline'}) for user_id in contact_ids}
    emit('contact_statuses', statuses)

@socketio.on('send_message')
def handle_send_message_event(data):
    conversation_id = data['conversation_id']
    Messages.save_message(conversation_id, data['sender_id'], data['message'])
    data['conversation_id'] = conversation_id
    socketio.emit('receive_message', data, room=conversation_id)

@socketio.on('join_conversation')
def handle_join_conversation_event(data):
    join_room(data['conversation_id'])
    socketio.emit('join_conversation_announcement', data, room=data['conversation_id'])

@socketio.on('leave_conversation')
def handle_leave_conversation_event(data):
    leave_room(data['conversation_id'])
    socketio.emit('leave_conversation_announcement', data, room=data['conversation_id'])

@socketio.on('call_user')
def handle_call_user(data):
    emit('receive_call', data, room=data['conversation_id'])

@socketio.on('answer_call')
def handle_answer_call(data):
    emit('call_answered', data, room=data['conversation_id'])

@socketio.on('ice_candidate')
def handle_ice_candidate(data):
    emit('ice_candidate', data, room=data['conversation_id'])
    