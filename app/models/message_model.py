from app.db import Database
from app.models.conversation_participants_model import ConversationParticipant


class Messages:
    def __init__(self, id, sender, message, sending_time, delivered_time, read_time, sender_id, conversation_id, create_at):
        self.id=id
        self.sender=sender
        self.message=message
        self.sending_time=sending_time
        self.delivered_time=delivered_time
        self.read_time=read_time
        self.sender_id=sender_id
        self.conversation_id=conversation_id
        self.create_at=create_at

    @staticmethod
    def save_message(conversation_id, sender_id, message):
        print(conversation_id, 'printing conversaio_id in save message')
        print(sender_id, 'printing sender_id in save message')
        print(message, 'printing message in save message')
        db = Database()
        ConversationParticipant.create_new_conversation_partcipent(sender_id, conversation_id)
        db.execute('''
            INSERT INTO messages (conversation_id, sender, message, sending_time, created_at, sender_id)
            VALUES (%s, %s, %s, NOW(), NOW(), %s)
        ''', (conversation_id, sender_id, message, sender_id))
        db.commit()
        db.close()