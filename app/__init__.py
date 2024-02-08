from flask import Flask, render_template,request, redirect, url_for
from flask_socketio import SocketIO, emit
import requests
from requests_toolbelt.multipart.encoder import MultipartEncoder
import json

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)
if __name__ == '__main__':
    socketio.run(app)

users = {}

@app.route('/')
def index(name='', phone=''):
    name = name
    phone=phone
    return render_template('common/landing.html', name=name, phone=phone)


@app.route('/about')
def about():
    return render_template('common/about.html')

@app.route('/login', methods=['GET','POST'])
def login(): #Method to call a formdata API
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        url = "http://117.20.28.178:8038/customerFaciliationPortal/signIn"

        payload = {
            'userId': username,
            'password': password
        }

        # Encode payload as multipart form-data
        multipart_data = MultipartEncoder(fields=payload)

        headers = {
            'Content-Type': multipart_data.content_type
        }

        response = requests.post(url, headers=headers, data=multipart_data)
        response_json = response.json()
        if(response_json['status'] == '200'):
            name =  response_json['name']
            phone =  response_json['phoneNo']
            return redirect(url_for('index', name=name, phone=phone))
        else:
            message = response_json['message']
            return render_template('authentication/login.html', message=message)
        
    elif request.method == 'GET':
        return render_template('authentication/login.html')

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