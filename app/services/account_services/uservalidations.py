import re

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