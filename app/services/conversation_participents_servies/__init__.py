from app.db import Database
from app.services.conversation_services import get_conversation

def createNewConversationPartcipent(user_id, conversation_id):
    conversationExisting = getConversationParticipent(user_id, conversation_id)
    if conversationExisting ==  None:
        db = Database()
        db.execute('INSERT INTO CONVERSATION_PARTICIPANTS (user_id, conversation_id, joined_at) values (%s, %s, NOW())', (user_id, conversation_id,))
        db.commit()
        db.close()

def addReceiverInConversationParticipents(receiver_id, conversation_id):
    conversationExisting = get_conversation(conversation_id)
    if conversationExisting:
        db = Database()
        db.execute('INSERT INTO CONVERSATION_PARTICIPANTS (user_id, conversation_id, joined_at) values (%s, %s, NOW())', (receiver_id, conversation_id,))
        db.commit()
        db.close()

def getConversationParticipent(user_id, conversation_id):
    db = Database()
    print(conversation_id, 'printing conversation id')
    db.execute('SELECT * from CONVERSATION_PARTICIPANTS where user_id = %s AND conversation_id = %s', (user_id, conversation_id,))
    conversation = db.fetchone()
    return conversation