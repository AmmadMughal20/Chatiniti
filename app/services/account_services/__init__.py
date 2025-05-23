import re
from app.db import Database


def userIdAlreadyExists(id):
    db = Database()
    db.execute("""Select userId from USERS where userId = (%s)""", (id,))
    userId = db.fetchone()
    db.close()
    return userId

def emailAlreadyExists(email):
    db = Database()
    db.execute("""Select email from USERS where email = (%s)""", (email,))
    email = db.fetchone()
    db.close()
    return email

def phoneAlreadyExists(phone):
    db = Database()
    db.execute("""Select phone from USERS where phone = (%s)""", (phone,))
    phone = db.fetchone()
    db.close()
    return phone

def titleAlreadyExists(title):
    db = Database()
    db.execute("""Select title from ROLES where title = (%s)""", (title,))
    title = db.fetchone()
    db.close()
    return title

def emailAlreadyExistsForUpdating(email):
    db = Database()
    db.execute("""Select userId from USERS where email = (%s)""", (email,))
    userId = db.fetchone()
    db.close()
    return userId

def phoneAlreadyExistsForUpdating(phone):
    db = Database()
    db.execute("""Select userId from USERS where phone = (%s)""", (phone,))
    userId = db.fetchone()
    db.close()
    return userId

def roleExists(roleId):
    db = Database()
    db.execute("""Select * from ROLES where roleId = (%s)""", (roleId,))
    role = db.fetchone()
    db.close()
    return role 
  
def authenticate_user_with_email(email, password):
    email_validation = validate_email(email)
    if email_validation == 1:
        return 1
    elif email_validation == 2:
        return 2

    password_validation = validate_password(password)

    if password_validation == 1:
        return 3

    elif email_validation == 0 and password_validation == 0:
        user = get_user_from_db_by_email_password(email, password)
        if user is None:
            return 4
        else:
            return user

def authenticate_User_With_User_Id(userId, password):
    userIdValidation = validate_user_id(userId)
    if userIdValidation == 1:
        return 1

    passwordValidation = validate_password(password)

    if passwordValidation == 1:
        return 2

    elif userIdValidation == 0 and passwordValidation == 0:
        authenticateUser = get_user_from_db_by_user_id_password(userId, password)
        if authenticateUser == None:
            return 3
        elif authenticateUser[6] == False:
            return 4
        else:
            return authenticateUser

def authenticate_user_with_user_id(user_id, password):
    user_id_validation = validate_user_id(user_id)
    if user_id_validation == 1:
        return 1

    password_validation = validate_password(password)

    if password_validation == 1:
        return 2

    elif user_id_validation == 0 and password_validation == 0:
        user = get_user_from_db_by_user_id_password(user_id, password)
        if user is None:
            return 3
        elif not user[0]["is_verified"]:
            return 4
        else:
            return user

def get_user_from_db_by_email_password(email, password):
    db = Database()
    query = """SELECT * FROM USERS WHERE email=%s AND password=%s"""
    db.execute(query, (email, password))
    user = db.fetchone()
    db.close()
    return user

def get_user_from_db_by_user_id_password(user_id, password):
    db = Database()
    query = """SELECT userId, name, age, email, phone, roleId, is_verified FROM USERS WHERE userId=%s AND password=%s"""
    db.execute(query, (user_id, password))
    user = db.fetchone()
    db.close()
    return user

def get_user_from_db_by_user_id(user_id):
    db = Database()
    query = """SELECT userId, email, is_verified FROM USERS WHERE userId=%s"""
    db.execute(query, (user_id,))
    user = db.fetchone()
    db.close()
    return user

def get_user_by_token(token):
    db = Database()
    query = """SELECT * FROM USERS WHERE token = %s"""
    db.execute(query, (token,))
    user = db.fetchone()
    db.close()
    return user

def update_password_by_token(token, password):
    is_valid_password = validate_password(password)
    if is_valid_password == 0:
        user = get_user_by_token(token)
        if user:
            db = Database()
            query = """UPDATE USERS SET password = %s WHERE token = %s"""
            db.execute(query, (password, token))
            db.commit()
            db.close()
            return 1
        else:
            return 2
    else:
        return 3



def validate_email(email):
    email_regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
    if email == '':
        return 1
    elif not re.match(email_regex, email):
        return 2
    else:
        return 0
    
def validate_user_id(user_id):
    if user_id == '':
        return 1
    else:
        return 0

def validate_password(password):
    if password == '':
        return 1
    else:
        return 0





