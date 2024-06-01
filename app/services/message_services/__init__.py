# Function to save a message
from app.db import Database

def save_message(conversation_id, sender_id, message):
    db = Database()
    if conversation_id == None:
        queryToCreateConversation = 'INSERT INTO CONVERSATIONS ()'
    db.execute('''
        INSERT INTO messages (conversation_id, sender, message, sending_time, created_at, sender_id)
        VALUES (%s, %s, %s, NOW(), NOW(), %s)
    ''', (conversation_id, sender_id, message, sender_id))
    db.commit()
    db.close()
