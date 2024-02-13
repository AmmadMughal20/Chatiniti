import re

def validateEmail(email):
    emailRegex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
    if email == '':
        return 1
    elif bool(re.match(emailRegex, email)) == False:
        return 2
    else:
        return 0
    
def validatePassword(password):
    if password == '':
        return 1
    else:
        return 0