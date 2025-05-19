from app.db import Database


class ConversationParticipant:
    def __init__(self, user_id, conversation_id, joined_at):
        self.user_id = user_id
        self.conversation_id = conversation_id
        self.joined_at = joined_at

    @staticmethod
    def create_new_conversation_partcipent(user_id, conversation_id):
        conversationExisting = ConversationParticipant.get_conversation_participant(user_id, conversation_id)
        if conversationExisting ==  None:
            db = Database()
            db.execute('INSERT INTO CONVERSATION_PARTICIPANTS (user_id, conversation_id, joined_at) values (%s, %s, NOW())', (user_id, conversation_id,))
            db.commit()
            db.close()

    @staticmethod
    def get_conversation_participant(user_id, conversation_id):
        db = Database()
        db.execute('SELECT * from CONVERSATION_PARTICIPANTS where user_id = %s AND conversation_id = %s', (user_id, conversation_id,))
        conversation_participant = db.fetchone()
        if conversation_participant:
            return ConversationParticipant(*conversation_participant)
        else:
            return None

    