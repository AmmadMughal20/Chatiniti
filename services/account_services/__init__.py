from db import db_connection
import re

def authenticateUserWithEmail(email, password):
    emailValidation = validateEmail(email)
    if emailValidation == 1:
        return 1
    elif emailValidation == 2:
        return 2

    passwordValidation = validatePassword(password)

    if passwordValidation == 1:
        return 3

    elif emailValidation == 0 and passwordValidation == 0:
        authenticateUser = getUserFromDbByEmailPassword(email, password)
        if authenticateUser == None:
            return 4
        else:
            return authenticateUser

def authenticateUserWithUserId(userId, password):
    userIdValidation = validateUserId(userId)
    if userIdValidation == 1:
        return 1

    passwordValidation = validatePassword(password)

    if passwordValidation == 1:
        return 2

    elif userIdValidation == 0 and passwordValidation == 0:
        authenticateUser = getUserFromDbByUserIdPassword(userId, password)
        if authenticateUser == None:
            return 3
        elif authenticateUser[0]["is_verified"] == False:
            return 4
        else:
            print(authenticateUser)
            return authenticateUser

def getUserFromDbByEmailPassword(email, password):
    connection = db_connection()
    cursor = connection.cursor()
    userByEmailPasswordQry = """SELECT * FROM USERS where email=%s AND password=%s"""
    cursor.execute(userByEmailPasswordQry, (email, password))
    user = [
        {
            'userId': row['userId'],
            'name': row['name'],
            'age': row['age'],
            'email': row['email'],
            'phone': row['phone'],
            'roleId': row['roleId']
        }
        for row in cursor.fetchall()
    ]
    if len(user) <= 0:
        return None
    else:
        return user

def getUserFromDbByUserIdPassword(userId, password):
    connection = db_connection()
    cursor = connection.cursor()
    userByUserIdPasswordQry = """SELECT userId, name, age, email, phone, roleId, is_verified FROM USERS WHERE userId=%s AND password=%s"""
    cursor.execute(userByUserIdPasswordQry, (userId, password))
    user = [
        {
            'userId': row[0],
            'name': row[1],
            'age': row[2],
            'email': row[3],
            'phone': row[4],
            'roleId': row[5],
            'is_verified': row[6]
        }
        for row in cursor.fetchall()
    ]
    if len(user) <= 0:
        return None
    else:
        return user

def getUserFromDbByUserId(userId):
    connection = db_connection()
    cursor = connection.cursor()
    userByUserIdQry = """SELECT userId, email, is_verified FROM USERS WHERE userId=%s """
    cursor.execute(userByUserIdQry, (userId,))
    user = [
        {
            'userId': row[0],
            'email': row[1],
            'is_verified': row[2]
        }
        for row in cursor.fetchall()
    ]
    if len(user) <= 0:
        return None
    else:
        return user

def getUserbyToken(token):
    conn = db_connection()  # Establish a connection to the database
    curs = conn.cursor()

    # Fetch the user associated with the token
    curs.execute("SELECT * FROM USERS WHERE token = %s", (token,))
    user = curs.fetchone()
    
    if len(user) <= 0:
        return None
    else:
        return user
  
def updatePasswordByToken(token, password):
    isValidPassword = validatePassword(password)  
    if isValidPassword == 0:
        isUserFound = getUserbyToken(token)
        if isUserFound:
            conn = db_connection()
            cur = conn.cursor()
            update_query = """UPDATE USERS SET password = %s WHERE token = %s"""
            cur.execute(update_query, (password, token))
            conn.commit()
            cur.close()
            conn.close()
            return 1
        else:
            return 2
    else:
        return 3
            
def validateEmail(email):
    emailRegex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
    if email == '':
        return 1
    elif bool(re.match(emailRegex, email)) == False:
        return 2
    else:
        return 0
    
def validateUserId(userId):
    if userId == '':
        return 1
    else:
        return 0

def validatePassword(password):
    if password == '':
        return 1
    else:
        return 0