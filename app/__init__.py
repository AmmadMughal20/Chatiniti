from flask import Flask, render_template,request, redirect, url_for, jsonify
from flask_socketio import SocketIO, emit
import requests
from requests_toolbelt.multipart.encoder import MultipartEncoder
from validations import validate_userId, validate_roleTitle, validate_userName, validate_age, validate_email, validate_phone, validate_password, validate_email_for_update, validate_phone_for_update, validate_role
from flask_cors import CORS
from db import db_connection
from services.account_services import authenticateUserWithEmail, authenticateUserWithUserId
import random
from flask_mail import Mail, Message

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SECRET_KEY'] = 'secret!'


app.config['MAIL_SERVER'] = 'smtp-relay.sendinblue.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = 'ammadmughal567@gmail.com'
app.config['MAIL_PASSWORD'] = 'FkWK2r0sAvBSP5Hy'
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False


socketio = SocketIO(app, cors_allowed_origins="*")
CORS(app)  # Allow all origins

mail = Mail(app)

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

@app.route('/loginAPI', methods=['GET','POST'])
def loginAPI(): #Method to call a formdata API
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
    
@socketio.on('disconnect')
def handle_disconnect():
    print('user disconnected')
    
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
    

def send_otp_Mail(user_name):
    random_number = random.randint(1000, 9999)
    msg = Message('Your One Time Password (OTP) for Takra!',
                  sender='ammadmughal567@gmail.com', recipients=['ammadmughal567@outlook.com'])
    msg.body = f"Hey {user_name}! Your one time password (OTP) for Takra account is: {random_number}."
    mail.send(msg)
    return random_number

@app.route('/signin', methods=['POST'])
def signIn():
    userId = request.form['userId']
    email = request.form['email']
    password = request.form['password']

    responseObject = {}

    if email != '':
        userAuthentication = authenticateUserWithEmail(email, password)

        if userAuthentication == 1:
            responseObject["status"] = 401
            responseObject["message"] = f"Email is required!"

        elif userAuthentication == 2:
            responseObject["status"] = 402
            responseObject["message"] = f"Invalid email!"

        elif userAuthentication == 3:
            responseObject["status"] = 403
            responseObject["message"] = f"Password is required!"

        elif userAuthentication == 4:
            responseObject["status"] = 404
            responseObject["message"] = f"Wrond email or password!"
        else:
            responseObject["status"] = 200
            responseObject["message"] = f"Data received successfully!"
            responseObject["data"] = userAuthentication

        return jsonify(responseObject)

    elif userId != '':
        userAuthentication = authenticateUserWithUserId(userId, password)

        if userAuthentication == 1:
            responseObject["status"] = 401
            responseObject["message"] = f"UserId is required!"

        elif userAuthentication == 2:
            responseObject["status"] = 402
            responseObject["message"] = f"Password is required!"

        elif userAuthentication == 3:
            responseObject["status"] = 403
            responseObject["message"] = f"Wrond userId or password!"
        else:
            responseObject["status"] = 200
            responseObject["message"] = f"Data received successfully!"
            responseObject["data"] = userAuthentication

    else:
        responseObject["status"] = 404
        responseObject["message"] = f"UserId or email is required!"

    return jsonify(responseObject)

@app.route('/users', methods=['GET', 'POST'])
def users():
    connec = db_connection()
    curs = connec.cursor()
    responseObject = {}

    if request.method == 'GET':
        allUsersQry = """SELECT * FROM USERS"""
        curs.execute(allUsersQry)
        users = [
            {
                'userId': row['userId'],
                'name': row['name'],
                'age': row['age'],
                'email': row['email'],
                'phone': row['phone'],
                'roleId': row['roleId']
            }
            for row in curs.fetchall()
        ]

        if len(users) > 0:
            responseObject["status"] = 200
            responseObject["data"] = users
            responseObject["message"] = "Data received successfully!"
        else:
            responseObject["status"] = 404
            responseObject["data"] = users
            responseObject["message"] = "No users found!"
        return jsonify(responseObject)

    if request.method == 'POST':
        new_user_id = request.form['userId']
        new_user_name = request.form['name']
        new_user_age = request.form['age']
        new_user_email = request.form['email']
        new_user_phone = request.form['phone']
        new_user_password = request.form['password']
        new_user_role = request.form['roleId']

        userIdValidation = validate_userId(new_user_id)

        if userIdValidation == 1:
            responseObject["status"] = 401
            responseObject["message"] = f"UserId already exists!"
            return jsonify(responseObject)

        userNameValidation = validate_userName(new_user_name)

        if userNameValidation == 1:
            responseObject["status"] = 402
            responseObject["message"] = f"Username can not be empty!"
            return jsonify(responseObject)
        elif userNameValidation == 2:
            responseObject["status"] = 403
            responseObject["message"] = f"Username can not contain special characters!"
            return jsonify(responseObject)

        userAgeValidation = validate_age(new_user_age)

        if userAgeValidation == 1:
            responseObject["status"] = 404
            responseObject["message"] = f"Age can contain numbers only!"
            return jsonify(responseObject)
        elif userAgeValidation == 2:
            responseObject["status"] = 405
            responseObject["message"] = f"Age can not be 0 or empty!"
            return jsonify(responseObject)

        userEmailValidation = validate_email(new_user_email)

        if userEmailValidation == 1:
            responseObject["status"] = 406
            responseObject["message"] = f"Email already exists!"
            return jsonify(responseObject)
        elif userEmailValidation == 2:
            responseObject["status"] = 407
            responseObject["message"] = f"Email can not be empty!"
            return jsonify(responseObject)
        elif userEmailValidation == 3:
            responseObject["status"] = 408
            responseObject["message"] = f"Invalid email format!"
            return jsonify(responseObject)

        userPhoneValidation = validate_phone(new_user_phone)

        if userPhoneValidation == 1:
            responseObject["status"] = 409
            responseObject["message"] = f"Phone already exists!"
            return jsonify(responseObject)
        elif userPhoneValidation == 2:
            responseObject["status"] = 410
            responseObject["message"] = f"Phone can not be empty!"
            return jsonify(responseObject)
        elif userPhoneValidation == 3:
            responseObject["status"] = 411
            responseObject["message"] = f"Invalid phone number!"
            return jsonify(responseObject)

        userPasswordValidation = validate_password(new_user_password)

        if userPasswordValidation == 1:
            responseObject["status"] = 412
            responseObject["message"] = f"Phone can not be empty!"
            return jsonify(responseObject)
        elif userPasswordValidation == 2:
            responseObject["status"] = 413
            responseObject["message"] = f"Password must contain atleast 8 characters including capital, small alphabets and numeric digits!"
            return jsonify(responseObject)

        userRoleValidation = validate_role(new_user_role)

        if userRoleValidation == 1:
            responseObject["status"] = 414
            responseObject["message"] = f"Role doesn't exists. Enter correct role id!"
            return jsonify(responseObject)

        if userIdValidation == 0 and userNameValidation == 0 and userAgeValidation == 0 and userEmailValidation == 0 and userPhoneValidation == 0 and userPasswordValidation == 0 and userRoleValidation == 0:
            print(request.form["status"])
            if request.form["status"] == '1':
                otp = send_otp_Mail(request.form['name'])
                responseObject["status"] = 200
                responseObject["OTP"] = otp
                responseObject["message"] = f"OTP sent successfully to user on email!"
                return jsonify(responseObject)

            elif request.form["status"] == '2':
                insertBookSqlQuery = """INSERT INTO USERS (userId, name, age, email, phone, password, roleId) VALUES (%s, %s, %s, %s, %s, %s, %s)"""
                curs.execute(
                    insertBookSqlQuery,
                    (
                        new_user_id,
                        new_user_name,
                        new_user_age,
                        new_user_email,
                        new_user_phone,
                        new_user_password,
                        new_user_role
                    )
                )
                connec.commit()
                responseObject["status"] = 200
                responseObject["message"] = f"User registered successfully!"
                return jsonify(responseObject)
            
            else:
                responseObject["status"] = 415
                responseObject["message"] = f"Some error occured!"
                return jsonify(responseObject)

        else:
            responseObject["status"] = 415
            responseObject["message"] = f"Some error occured!"
            return jsonify(responseObject)
        
        
@app.route('/roles', methods=['GET', 'POST'])
def roles():
    connec = db_connection()
    curs = connec.cursor()
    responseObject = {}

    if request.method == 'GET':
        allRolesQry = """SELECT * FROM ROLES"""
        curs.execute(allRolesQry)
        roles = [
            {
                'roleId': row['roleId'],
                'title': row['title'],
            }
            for row in curs.fetchall()
        ]

        if len(roles) > 0:
            responseObject["status"] = 200
            responseObject["data"] = roles
            responseObject["message"] = "Data received successfully!"
        else:
            responseObject["status"] = 404
            responseObject["data"] = roles
            responseObject["message"] = "No role found!"
        return jsonify(responseObject)

    if request.method == 'POST':
        new_role_title = request.form['title']
        titleValidation = validate_roleTitle(new_role_title)
        if titleValidation == 1:
            responseObject["status"] = 200
            responseObject["message"] = f"Role already exists!"
            return jsonify(responseObject)
        elif titleValidation == 0:
            insertRoleSqlQuery = """INSERT INTO ROLES (title) VALUES (%s)"""
            curs.execute(
                insertRoleSqlQuery,
                (
                    new_role_title,
                )
            )
            connec.commit()
            responseObject["status"] = 200
            responseObject["message"] = f"Role added successfully!"
            return jsonify(responseObject)

