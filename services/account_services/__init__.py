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
        else:
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
    userByUserIdPasswordQry = """SELECT * FROM USERS where userId=%s AND password=%s"""
    cursor.execute(userByUserIdPasswordQry, (userId, password))
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