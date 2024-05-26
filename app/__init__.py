from flask import Flask, render_template,request, redirect, url_for, jsonify, flash, session
from flask_socketio import SocketIO, emit
import requests
from requests_toolbelt.multipart.encoder import MultipartEncoder
from validations import validate_userId, validate_roleTitle, validate_userName, validate_age, validate_email, validate_phone, validate_password, validate_email_for_update, validate_phone_for_update, validate_role
from flask_cors import CORS
from db import db_connection
from services.account_services import authenticateUserWithEmail, authenticateUserWithUserId, getUserFromDbByUserId, getUserbyToken, updatePasswordByToken
import random
from flask_mail import Mail, Message
import secrets
import random
from faker import Faker

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

faker = Faker()


if __name__ == '__main__':
    socketio.run(app)

users = {}
contacts = [
    {"id": 0, "name": "John Doe", "image": "https://via.placeholder.com/150"},
    {"id": 1, "name": "Jane Smith", "image": "https://via.placeholder.com/150"},
    {"id": 2, "name": "Alice Johnson", "image": "https://via.placeholder.com/150"},
    {"id": 3, "name": "Michael Brown", "image": "https://via.placeholder.com/150"},
    {"id": 4, "name": "Emily Davis", "image": "https://via.placeholder.com/150"},
    {"id": 5, "name": "William Wilson", "image": "https://via.placeholder.com/150"},
    {"id": 6, "name": "Emma Taylor", "image": "https://via.placeholder.com/150"},
    {"id": 7, "name": "Matthew Moore", "image": "https://via.placeholder.com/150"},
    {"id": 8, "name": "Olivia Anderson", "image": "https://via.placeholder.com/150"},
    {"id": 9, "name": "James White", "image": "https://via.placeholder.com/150"},
    {"id": 10, "name": "Sophia Martinez", "image": "https://via.placeholder.com/150"},
    {"id": 11, "name": "David Thompson", "image": "https://via.placeholder.com/150"},
    {"id": 12, "name": "Isabella Harris", "image": "https://via.placeholder.com/150"},
    {"id": 13, "name": "Daniel Young", "image": "https://via.placeholder.com/150"},
    {"id": 14, "name": "Amelia Clark", "image": "https://via.placeholder.com/150"},
    {"id": 15, "name": "Joseph Lewis", "image": "https://via.placeholder.com/150"},
    {"id": 16, "name": "Charlotte Allen", "image": "https://via.placeholder.com/150"},
    {"id": 17, "name": "Benjamin King", "image": "https://via.placeholder.com/150"},
    {"id": 18, "name": "Mia Wright", "image": "https://via.placeholder.com/150"},
    {"id": 19, "name": "Andrew Scott", "image": "https://via.placeholder.com/150"},
    {"id": 20, "name": "Harper Hill", "image": "https://via.placeholder.com/150"},
    {"id": 21, "name": "Matthew Garcia", "image": "https://via.placeholder.com/150"},
    {"id": 22, "name": "Evelyn Lee", "image": "https://via.placeholder.com/150"},
    {"id": 23, "name": "William Walker", "image": "https://via.placeholder.com/150"},
    {"id": 24, "name": "Abigail Perez", "image": "https://via.placeholder.com/150"},
    {"id": 25, "name": "Alexander Hall", "image": "https://via.placeholder.com/150"},
    {"id": 26, "name": "Emily Hernandez", "image": "https://via.placeholder.com/150"},
    {"id": 27, "name": "Daniel Green", "image": "https://via.placeholder.com/150"},
    {"id": 28, "name": "Madison Carter", "image": "https://via.placeholder.com/150"},
    {"id": 29, "name": "Josephine Adams", "image": "https://via.placeholder.com/150"},
]

def generate_chat_history(num_chats):
    chat_history = {}
    for i in range(0, num_chats):
        chat_history[i] = []
        senders = ["You", faker.name()]  # Initialize sender list with "You" and a random name
        for _ in range(random.randint(5, 20)):  # Generate random number of messages for each chat
            sender = senders.pop(0)  # Alternate sender names
            senders.append(sender)  # Add the sender back to the list
            message = {
                "sender": sender,
                "message": faker.sentence(),
                "sendingTime": faker.time(pattern='%I:%M %p'),
                "deliveredTime": faker.time(pattern='%I:%M %p'),
                "readTime": faker.time(pattern='%I:%M %p')
            }
            chat_history[i].append(message)
    return chat_history

chat_history = generate_chat_history(30)


@app.route('/')
def index(name='', phone=''):
    name = name
    phone=phone
    return render_template('common/landing.html', name=name, phone=phone)

@app.route('/about')
def about():
    return render_template('common/about.html')

@app.route('/signin', methods=['GET','POST'])
def signIn():
    if request.method == 'GET':
        return render_template('authentication/login.html')
    
    elif request.method == 'POST':
        
        userId = request.form['userId']
        password = request.form['password']

        responseObject = {}
                
        if userId != '':
            userAuthentication = authenticateUserWithUserId(userId, password)

            if userAuthentication == 1:
                responseObject["status"] = 401
                responseObject["message"] = f"UserId is required!"

            elif userAuthentication == 2:
                responseObject["status"] = 402
                responseObject["message"] = f"Password is required!"

            elif userAuthentication == 3:
                responseObject["status"] = 403
                responseObject["message"] = f"Wrong userId or password!"
            elif userAuthentication == 4:
                responseObject["status"] = 404
                responseObject["message"] = f"Email not verified yet!"
            else:
                session['user_id'] = userAuthentication[0]["userId"]
                session['name'] = userAuthentication[0]["name"]
                session['phone'] = userAuthentication[0]["phone"]
                session['email'] = userAuthentication[0]["email"]
                session['roleId'] = userAuthentication[0]["roleId"]
                responseObject["status"] = 200
                responseObject["message"] = f"Data received successfully!"
                responseObject["data"] = userAuthentication
        else:
            responseObject["status"] = 404
            responseObject["message"] = f"UserId is required!"
            
        if responseObject["status"] == 200:
            return redirect(url_for('index'))
        else:
            return render_template('authentication/login.html', error=responseObject)

def createUser(userId, name, age, email, phoneNo, password, role):
    token = secrets.token_urlsafe(16)
    sendVerificationEmail(email, token)
    flash('An email has been sent to verify your account.')  # Flash message here
    connec = db_connection()
    curs = connec.cursor()
    insertBookSqlQuery = """INSERT INTO USERS (userId, name, age, email, phone, password, roleId, token) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"""
    curs.execute(insertBookSqlQuery,
                    (
                        userId,
                        name,
                        age,
                        email,
                        phoneNo,
                        password,
                        role,
                        token
                    )
                )
    connec.commit()
                
    return redirect(url_for('signIn'))

def sendVerificationEmail(email, token):
    # Replace with actual email sending logic using Flask-Mail
    verification_link = url_for('verify_email', token=token, _external=True)
    msg = Message('Verify your email', sender='your_email@example.com', recipients=[email])
    msg.body = f'Click the following link to verify your email: {verification_link}'
    mail.send(msg)
          
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'GET':
        return render_template('authentication/signup.html')
    if request.method == 'POST':
        new_user_id = request.form['userId']
        new_user_name = request.form['name']
        new_user_age = request.form['age']
        new_user_email = request.form['email']
        new_user_phone = request.form['phone']
        new_user_password = request.form['password']
        new_user_role = request.form['roleId']
        responseObject = {}

        userIdValidation = validate_userId(new_user_id)

        if userIdValidation == 1:
            responseObject["status"] = 401
            responseObject["message"] = f"UserId already exists!"

        userNameValidation = validate_userName(new_user_name)

        if userNameValidation == 1:
            responseObject["status"] = 402
            responseObject["message"] = f"Username can not be empty!"
        elif userNameValidation == 2:
            responseObject["status"] = 403
            responseObject["message"] = f"Username can not contain special characters!"

        userAgeValidation = validate_age(new_user_age)

        if userAgeValidation == 1:
            responseObject["status"] = 404
            responseObject["message"] = f"Age can contain numbers only!"
        elif userAgeValidation == 2:
            responseObject["status"] = 405
            responseObject["message"] = f"Age can not be 0 or empty!"

        userEmailValidation = validate_email(new_user_email)

        if userEmailValidation == 1:
            responseObject["status"] = 406
            responseObject["message"] = f"Email already exists!"
        elif userEmailValidation == 2:
            responseObject["status"] = 407
            responseObject["message"] = f"Email can not be empty!"
        elif userEmailValidation == 3:
            responseObject["status"] = 408
            responseObject["message"] = f"Invalid email format!"

        userPhoneValidation = validate_phone(new_user_phone)

        if userPhoneValidation == 1:
            responseObject["status"] = 409
            responseObject["message"] = f"Phone already exists!"
        elif userPhoneValidation == 2:
            responseObject["status"] = 410
            responseObject["message"] = f"Phone can not be empty!"
        elif userPhoneValidation == 3:
            responseObject["status"] = 411
            responseObject["message"] = f"Invalid phone number!"

        userPasswordValidation = validate_password(new_user_password)

        if userPasswordValidation == 1:
            responseObject["status"] = 412
            responseObject["message"] = f"Phone can not be empty!"
        elif userPasswordValidation == 2:
            responseObject["status"] = 413
            responseObject["message"] = f"Password must contain atleast 8 characters including capital, small alphabets and numeric digits!"

        userRoleValidation = validate_role(new_user_role)

        if userRoleValidation == 1:
            responseObject["status"] = 414
            responseObject["message"] = f"Role doesn't exists. Enter correct role id!"

        if userIdValidation == 0 and userNameValidation == 0 and userAgeValidation == 0 and userEmailValidation == 0 and userPhoneValidation == 0 and userPasswordValidation == 0 and userRoleValidation == 0:
            return createUser(new_user_id, new_user_name, new_user_age, new_user_email, new_user_phone, new_user_password, new_user_role)

        if responseObject["status"] != 200:
            return render_template('authentication/signup.html', error=responseObject["message"])

@app.route('/verify_email/<token>')
def verify_email(token):
    conn = db_connection()  # Establish a connection to the database
    curs = conn.cursor()

    # Fetch the user associated with the token
    curs.execute("SELECT * FROM USERS WHERE token = %s", (token,))
    user = curs.fetchone()

    if user:
        # Update the is_verified field for the user
        curs.execute("UPDATE USERS SET is_verified = TRUE WHERE userId = %s", (user[0],))
        conn.commit()  # Commit the transaction

        flash('Your email has been verified successfully.')
        return redirect(url_for('signIn'))
    else:
        flash('Invalid verification token.')
        return redirect(url_for('signIn'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('signIn'))

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
    index = request.args.get('contact_id', default=0, type=int)
    chat_hist = getChatByIndex(index)
    contactName = contacts[index]["name"]    
    return render_template('common/chat.html', contacts=contacts, chat_history=chat_hist, contactName=contactName)

def getChatByIndex(index):
    return chat_history[index]
    
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


@app.route('/forgotpassword', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'GET':
        return render_template('authentication/forgotpassword.html')
    elif request.method == 'POST':
        user_id = request.form.get('userId')
        userFound = getUserFromDbByUserId(user_id)
        print(userFound)
        if userFound:
            recovery_token = generate_random_token()
            updateToken(user_id, recovery_token)
            send_recovery_email_to_user(userFound[0]['email'], recovery_token)
            flash('Recovery email sent. Please check your email.')
        else:
            flash('User ID not found.')

    return redirect(url_for('forgot_password'))

def updateToken(user_id, token):
    conn = db_connection()
    curs = conn.cursor()
    curs.execute("UPDATE USERS SET token = %s WHERE userId = %s", (token, user_id))
    conn.commit()  # Commit the transaction


def generate_random_token():
    # Generate a random 6-digit token
    return str(random.randint(100000, 999999))

def send_recovery_email_to_user(email, token):
    recovery_link = url_for('reset_password', token=token, _external=True)
    msg = Message('Verify your email', sender='your_email@example.com', recipients=[email])
    msg.body = f'Dear User,\n\nYou requested to reset your password. Please click on the following link to reset your password: {recovery_link}'
    mail.send(msg)

@app.route('/resetpassword', methods=['GET', 'POST'])
def reset_password():
    if request.method == 'GET':
        # Get the reset token from the URL query parameters
        token = request.args.get('token')
        if token:
            userFound = getUserbyToken(token)
            if userFound:
                return render_template('authentication/resetpassword.html', token=token)
            else:
                print('Invalid reset token.')
                flash('Invalid reset token.')
                return redirect(url_for('forgot_password'))
        else:
            print('Reset token not provided.')
            flash('Reset token not provided.')
            return redirect(url_for('forgot_password'))

    elif request.method == 'POST':
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']
        token = request.form['token']
        if new_password != confirm_password:
            print('Passwords do not match.')
            flash('Passwords do not match.')
            return redirect(url_for('reset_password', token=token))
        updatingPassword = updatePasswordByToken(token, new_password)
        if updatingPassword == 1:
            print('Password reset successfully.')
            flash('Password reset successfully.')
            return redirect(url_for('signIn'))
        elif updatingPassword == 2:
            print('Invalid reset token.')
            flash('Invalid reset token.')
            return redirect(url_for('forgot_password'))
        elif updatingPassword == 3:
            print('Invalid Password!')
            flash('Invalid Password!')
            return redirect(url_for('forgot_password'))