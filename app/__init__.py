from flask import Flask, render_template,request
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)
if __name__ == '__main__':
    socketio.run(app)

users = {}

@app.route('/')
def index():
    return render_template('common/index.html')


@app.route('/about')
def about():
    return render_template('common/about.html')


@app.route('/chat')
def chat():
    return render_template('common/chat.html')

@socketio.on('connect')
def handle_connect():
    print('user connected')
    
@socketio.on('user_join')
def handle_user_join(username):
    print(f"User {username} joined!")
    users[username] = request.sid
    
    
@socketio.on('new_message')
def handle_new_message(message):
    print(f"New message {message}")
    username = None
    for user in users:
        if users[user] == request.sid:
            username = user
    emit("chat", {"message": message, "username": username}, broadcast=True)