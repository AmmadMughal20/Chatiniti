from flask import request
from flask_socketio import emit, join_room, leave_room
import time
from app import socketio
from app.models.message_model import Messages
from app.services.conversation_services import create_new_conversation
from app.services.message_services import save_message

online_users = {}

@socketio.on('connect')
def handle_connect():
    user_id = request.args.get('user_id')
    print(user_id, 'printing user id')
    if user_id:
        online_users[user_id.strip()] = {'status': 'online', 'last_active': time.time()}
        print(online_users, 'printing online users')
        emit('user_status', {'user_id': user_id, 'status': 'online'}, broadcast=True)

@socketio.on('disconnect')
def handle_disconnect():
    user_id = request.args.get('user_id')
    if user_id in online_users:
        online_users[user_id]['status'] = 'offline'
        emit('user_status', {'user_id': user_id, 'status': 'offline'}, broadcast=True)

@socketio.on('started_typing')
def handle_start_typing(data):
    user_id = data['user_id']
    if user_id:
        online_users[user_id.strip()]['typing_status'] = True
        emit('user_typing_status', {'user_id': user_id, 'typing_status': True}, broadcast=True)

@socketio.on('stopped_typing')
def handle_stop_typing(data):
    user_id = data['user_id']
    if user_id in online_users:
        online_users[user_id]['typing_status'] = False
        emit('user_typing_status', {'user_id': user_id, 'typing_status': False}, broadcast=True)

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

# WebRTC signaling handlers
@socketio.on('call_user')
def handle_call_user(data):
    emit('receive_call', data, to=data['conversation_id'])

@socketio.on('answer_call')
def handle_answer_call(data):
    emit('call_answered', data, to=data['conversation_id'])

@socketio.on('ice_candidate')
def handle_ice_candidate(data):
    emit('ice_candidate', data, to=data['conversation_id'])

@socketio.on('end_call')
def handle_end_call(data):
    emit('call_ended', data, to=data['conversation_id'])

@socketio.on('reject_call')
def handle_reject_call(data):
    emit('call_rejected', data, to=data['conversation_id'])
    