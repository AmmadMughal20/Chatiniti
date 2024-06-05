import random
from flask import url_for
from flask_mail import Mail, Message

def sendVerificationEmail(email, token):
    # Replace with actual email sending logic using Flask-Mail
    from app import mail
    verification_link = url_for('authentication.verify_email', token=token, _external=True)
    msg = Message('Verify your email', sender='your_email@example.com', recipients=[email])
    msg.body = f'Click the following link to verify your email: {verification_link}'
    mail.send(msg)

def send_otp_Mail(user_name):
    from app import mail
    random_number = random.randint(1000, 9999)
    msg = Message('Your One Time Password (OTP) for Takra!',
                  sender='ammadmughal567@gmail.com', recipients=['ammadmughal567@outlook.com'])
    msg.body = f"Hey {user_name}! Your one time password (OTP) for Takra account is: {random_number}."
    mail.send(msg)
    return random_number

def get_conversation_id(conversations, recipient_id):
    for conversation in conversations:
        for participant in conversation['participants']:
            if participant['receiver_id'] == recipient_id:
                return conversation['conversation_id']
    return None  # If no match is found

def send_recovery_email_to_user(email, token):
    from app import mail
    recovery_link = url_for('authentication.reset_password', token=token, _external=True)
    msg = Message('Verify your email', sender='your_email@example.com', recipients=[email])
    msg.body = f'Dear User,\n\nYou requested to reset your password. Please click on the following link to reset your password: {recovery_link}'
    mail.send(msg)

def generate_random_token():
    # Generate a random 6-digit token
    return str(random.randint(100000, 999999))

def find_element(data, key, value):
    for item in data:
        if key in item and item[key] == value:
            return item
    return None


def find_latest_conversations(conversations):
    latest_conv = None

    for con in conversations:
        most_recent_message = max(con["messages"], key=lambda message: message["created_at"])
        con["most_recent_time"] = most_recent_message["created_at"]
            
    latest_conv = max(conversations, key=lambda conversation: conversation["most_recent_time"])
    return latest_conv