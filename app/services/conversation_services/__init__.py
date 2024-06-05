from app.db import Database

def create_new_conversation(userid, recepientid):
    db = Database()
    title = userid + ' ' + recepientid
    db.execute('INSERT INTO CONVERSATIONS (title, created_at) values (%s, NOW()) RETURNING id', (title,))
    new_conversation_id = db.fetchone()
    new_conversation_id = new_conversation_id[0]
    db.commit()
    db.close()
    return new_conversation_id


def get_conversation(conversation_id):
    db = Database()
    db.execute('Select id from conversations where id = %s', (conversation_id,))
    conversation_id = db.fetchone()
    db.close()
    if conversation_id:
        return conversation_id
    else:
        return None
    




