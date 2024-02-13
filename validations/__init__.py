from db import db_connection
import re

def validate_userId(id):
    userId = userIdAlreadyExists(id)
    if userId:
        return 1
    else:
        return 0

def validate_userName(userName):
    if userName == '' or userName == None:
        return 1
    elif bool(re.match('^[a-zA-Z0-9 ]*$', userName)) == False:
        return 2
    else:
        return 0

def validate_age(age):
    if bool(re.match('^[0-9]*$', age)) == False:
        return 1
    elif age == '' or age == None or int(age) == 0:
        return 2
    else:
        return 0
    
def validate_email(email):
    emailRegex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'

    emailInDb = emailAlreadyExists(email)

    if emailInDb:
        return 1
    elif email == '':
        return 2
    elif bool(re.match(emailRegex, email)) == False:
        return 3
    else:
        return 0
    
def validate_phone(phone):
    phoneRegex = r"^(03\d{9})$"

    phoneInDb = phoneAlreadyExists(phone)

    if phoneInDb:
        return 1
    elif phone == '':
        return 2
    elif bool(re.match(phoneRegex, phone)) == False:
        return 3
    else:
        return 0
    
def validate_password(password):
    passwordRegex = r"^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$"
    
    if password == '':
        return 1
    elif bool(re.match(passwordRegex, password)) == False:
        return 2
    else:
        return 0
    
def validate_role(roleId):

    roleInDb = roleExists(roleId)

    if not roleInDb:
        return 1
    else:
        return 0
    
def validate_email_for_update(email, userId):
    emailRegex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'

    idInDb = emailAlreadyExistsForUpdating(email)

    if email == '':
        return 2
    elif bool(re.match(emailRegex, email)) == False:
        return 3
    elif idInDb['userId'] != userId:
        return 1
    else:
        return 0
    
def validate_phone_for_update(phone, userId):
    phoneRegex = r"^(03\d{9})$"

    idInDb = phoneAlreadyExistsForUpdating(phone)

    if phone == '':
        return 2
    elif bool(re.match(phoneRegex, phone)) == False:
        return 3
    if idInDb['userId'] != userId:
        return 1
    else:
        return 0

def validate_roleTitle(title):
    titleInDb = titleAlreadyExists(title)
    if (titleInDb):
        return 1
    else:
        return 0

def userIdAlreadyExists(id):
    connection = db_connection()
    cursor = connection.cursor()
    cursor.execute("""Select userId from USERS where userId = (%s)""", (id,))
    userId = cursor.fetchone()
    connection.close()
    return userId

def emailAlreadyExists(email):
    connection = db_connection()
    cursor = connection.cursor()
    cursor.execute("""Select email from USERS where email = (%s)""", (email,))
    email = cursor.fetchone()
    connection.close()
    return email

def phoneAlreadyExists(phone):
    connection = db_connection()
    cursor = connection.cursor()
    cursor.execute("""Select phone from USERS where phone = (%s)""", (phone,))
    phone = cursor.fetchone()
    connection.close()
    return phone

def titleAlreadyExists(title):
    connection = db_connection()
    cursor = connection.cursor()
    cursor.execute("""Select title from ROLES where title = (%s)""", (title,))
    title = cursor.fetchone()
    connection.close()
    return title

def emailAlreadyExistsForUpdating(email):
    connection = db_connection()
    cursor = connection.cursor()
    cursor.execute("""Select userId from USERS where email = (%s)""", (email,))
    userId = cursor.fetchone()
    connection.close()
    return userId

def phoneAlreadyExistsForUpdating(phone):
    connection = db_connection()
    cursor = connection.cursor()
    cursor.execute("""Select userId from USERS where phone = (%s)""", (phone,))
    userId = cursor.fetchone()
    connection.close()
    return userId

def roleExists(roleId):
    connection = db_connection()
    cursor = connection.cursor()
    cursor.execute("""Select * from ROLES where roleId = (%s)""", (roleId,))
    role = cursor.fetchone()
    connection.close()
    return role