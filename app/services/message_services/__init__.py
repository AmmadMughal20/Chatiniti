# Function to save a message
from app.db import Database
from app.services.conversation_participents_servies import createNewConversationPartcipent
from app.services.conversation_services import create_new_conversation
import random

def save_message(conversation_id, sender_id, message):
    db = Database()
    createNewConversationPartcipent(sender_id, conversation_id)
    db.execute('''
        INSERT INTO messages (conversation_id, sender, message, sending_time, created_at, sender_id)
        VALUES (%s, %s, %s, NOW(), NOW(), %s)
    ''', (conversation_id, sender_id, message, sender_id))
    db.commit()
    db.close()
