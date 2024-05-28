from flask import Flask, render_template,request, redirect, url_for, jsonify, flash, session
from flask_socketio import SocketIO, emit
import requests
from requests_toolbelt.multipart.encoder import MultipartEncoder
from services.chat_services import get_conversations_and_participants, get_latest_conversation_with_participents, get_messages_by_conversation
from services.contact_services import add_user_contact, create_contact, delete_contact, get_contact, get_contacts, remove_user_contact, update_contact
from services.friendship_services import get_friends
from services.user_services import getUserById
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

@app.route('/chat', defaults={'recepent_id': None}, methods=['GET'])
@app.route('/chat/<recepent_id>', methods=['GET','PUT', 'DELETE'])
def chat(recepent_id=None):
    messagesconverted = []
    messages = []
    friends = []
    receiver = None
    contactName = None
    latestConversation = None
    if(session):
        user_id = session['user_id']
        friends = get_friends(user_id)   
        print(friends, 'printing friends')     
        conversations = get_conversations_and_participants(user_id)
        if recepent_id:
            receiver = getUserById(recepent_id)
            conversation_id = get_conversation_id(conversations, recepent_id)
            messages = get_messages_by_conversation(conversation_id)
        else:
            latestConversation = get_latest_conversation_with_participents(user_id)
            if latestConversation:
                conversation_id = latestConversation[0]['conversation_id']
                recepent_id = latestConversation[0]['participants'][0]['receiver_id']
                receiver = getUserById(recepent_id)
                messages = get_messages_by_conversation(conversation_id)
            
        for row in messages:
            if(row[6] == user_id):
                message = {
                    "sender": "You",
                    "message": row[2],
                    "sendingTime": row[3],
                    "deliveredTime": row[4],
                    "readTime": row[5]
                }
            else:
                message = {
                    "sender": row[6],
                    "message": row[2],
                    "sendingTime": row[3],
                    "deliveredTime": row[4],
                    "readTime": row[5]
                }
            messagesconverted.append(message)
        if receiver:
            contactName = receiver[1] + '  ' +receiver[0]
        
    return render_template('common/chat.html', contacts=friends, chat_history=messagesconverted, contactName=contactName)

def get_conversation_id(conversations, recipient_id):
    for conversation in conversations:
        for participant in conversation['participants']:
            if participant['receiver_id'] == recipient_id:
                return conversation['conversation_id']
    return None  # If no match is found

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
    users = []

    if 'user_id' in session:
        logged_in_user_id = session['user_id']

        if request.method == 'GET':
            allUsersQry = """
                SELECT u.userid, u.name, u.age, u.email, u.phone,
                       f.status, 
                       CASE
                           WHEN f.user_id1 = %s THEN 'requested'
                           WHEN f.user_id2 = %s THEN 'received'
                           ELSE 'none'
                       END AS friendship_direction
                FROM users u
                LEFT JOIN friendships f ON
                    (u.userid = f.user_id1 AND f.user_id2 = %s)
                    OR (u.userid = f.user_id2 AND f.user_id1 = %s)
            """
            curs.execute(allUsersQry, (logged_in_user_id, logged_in_user_id, logged_in_user_id, logged_in_user_id))
            usersArray = curs.fetchall()

            for row in usersArray:
                if row[0] != logged_in_user_id:
                    user = {
                        "userId": row[0],
                        "name": row[1],
                        "age": row[2],
                        "email": row[3],
                        "phone": row[4],
                        "friendship_status": row[5] if row[5] else 'None',
                        "friendship_direction": row[6]
                    }
                    users.append(user)

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

    return render_template('common/users.html', users=users)

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

@app.route('/contacts', defaults={'contact_id': None}, methods=['GET', 'POST', 'PUT'])
@app.route('/contacts/<int:contact_id>', methods=['PUT', 'DELETE'])
def contactsfunction(contact_id=None):
    print(request.method, 'printing request method')
    userIdToGetChats = session.get('user_id')

    if request.method == 'POST':
        if 'user_id' in session:
            firstName = request.form['first_name']
            middleName = request.form.get('middle_name', '')
            lastName = request.form['last_name']
            phone = request.form['phone']
            email = request.form['email']
            contact = {
                "first_name": firstName,
                "last_name": lastName,
                "middle_name": middleName,
                "phone": phone,
                "email": email
            }
            newContactId = create_contact(contact)
            saveContactInUserTable = add_user_contact(newContactId, userIdToGetChats)
            return redirect(url_for('contactsfunction'))

    if request.method == 'PUT':
        if 'user_id' not in session:
            return jsonify({'error': 'User not authenticated'}), 401
        contact_data = {
            "first_name": request.form['first_name'],
            "middle_name": request.form.get('middle_name', ''),
            "last_name": request.form['last_name'],
            "phone": request.form['phone'],
            "email": request.form['email']
        }

        update = update_contact(contact_id, contact_data)
        remove_user_contact(userIdToGetChats, contact_id)
        add_user_contact(contact_id, userIdToGetChats)
        contactsToDisplay = get_contacts(userIdToGetChats)
        return render_template('common/contacts.html', contacts=contactsToDisplay)

    if request.method == 'DELETE':
        if 'user_id' in session:
            removeContactResult = remove_user_contact(userIdToGetChats, contact_id)
            deleteContactResult = delete_contact(contact_id)
            if removeContactResult == 200 and deleteContactResult == 200:
                return jsonify({'message': 'Contact deleted successfully'}), 200
            else:
                return jsonify({'error': 'Failed to delete contact'}), 500
        return jsonify({'error': 'User not authenticated'}), 401

    if request.method == 'GET':
        if 'user_id' in session:
            contactsToDisplay = get_contacts(userIdToGetChats)
        else:
            contactsToDisplay = []
        return render_template('common/contacts.html', contacts=contactsToDisplay)

@app.route('/addFriend', methods=['POST'])
def addFriend():
    data = request.get_json()
    if session:
        user_id1 = session['user_id']  # Assuming the logged-in user's ID is 1; replace with actual logic
        user_id2 = data['user_id2']

    if user_id1 == user_id2:
        return jsonify({'success': False, 'message': "You can't be friends with yourself"}), 400

    try:
        conn = db_connection()
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO friendships (user_id1, user_id2, status)
            VALUES (%s, %s, 'pending')
            ON CONFLICT (user_id1, user_id2) DO NOTHING
            RETURNING friendship_id;
        """, (user_id1, user_id2))

        result = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()

        if result:
            return redirect(url_for('users'))
        else:
            return jsonify({'success': False, 'message': 'Friend request already exists'}), 400

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'success': False, 'message': 'An error occurred while sending friend request'}), 500

@app.route('/acceptFriend', methods=['POST'])
def acceptFriend():
    data = request.get_json()
    user_id1 = session['user_id']
    user_id2 = data['user_id']

    try:
        conn = db_connection()
        cur = conn.cursor()

        cur.execute("""
            UPDATE friendships
            SET status = 'accepted'
            WHERE (user_id1 = %s AND user_id2 = %s) OR (user_id1 = %s AND user_id2 = %s)
        """, (user_id2, user_id1, user_id1, user_id2))

        conn.commit()
        cur.close()
        conn.close()

        return redirect(url_for('users'))

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'success': False, 'message': 'An error occurred while accepting the friend request'}), 500

@app.route('/rejectFriend', methods=['POST'])
def rejectFriend():
    data = request.get_json()
    user_id1 = session['user_id']
    user_id2 = data['user_id']

    try:
        conn = db_connection()
        cur = conn.cursor()

        cur.execute("""
            UPDATE friendships
            SET status = 'rejected'
            WHERE (user_id1 = %s AND user_id2 = %s) OR (user_id1 = %s AND user_id2 = %s)
        """, (user_id2, user_id1, user_id1, user_id2))

        conn.commit()
        cur.close()
        conn.close()

        return redirect(url_for('users'))

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'success': False, 'message': 'An error occurred while rejecting the friend request'}), 500
