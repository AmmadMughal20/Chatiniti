from app.db import Database


def get_conversations_and_participants(sender_id):
    db = Database()

    sender_conversations_query = "Select distinct user_id, conversation_id, joined_at from conversation_participants where user_id = %s"
    db.execute(sender_conversations_query, (sender_id,))
    results = db.fetchall()

    conversations = []

    for result in results:
        conv = {
            "user_id1": result[0],
            "conversation_id": result[1],
            "joined_at1": result[2],
            }
        conversations.append(conv)

    for conv in conversations:
        conv_id = conv["conversation_id"]
        receiver_id = None
        receiver_id_query = "Select user_id, joined_at from conversation_participants where conversation_id = %s and user_id != %s"
        db.execute(receiver_id_query, (conv_id, sender_id,))
        result = db.fetchone()
        receiver_id = result[0]
        joined_at2 = result[1]
        conv["user_id2"] = receiver_id
        conv["joined_at2"] = joined_at2

        conv_title_query = "Select title from conversations where id = %s"
        db.execute(conv_title_query, (conv_id,))
        result = db.fetchone()
        conv["title"] = result[0]

        messages_query = "Select * from messages where conversation_id = %s"
        db.execute(messages_query, (conv_id,))
        result = db.fetchall()
        messages = []
        for res in result:
            message = {
                "message_id": res[0],
                "sender": res[1],
                "message": res[2],
                "sending_time": res[3],
                "delivered_time": res[4],
                "read_time": res[5],
                "sender_id": res[6],
                "conversation_id": res[7],
                "created_at": res[8],
                }
            messages.append(message)
        conv["messages"] = messages
        
    return conversations

def get_messages_by_conversation(conversation_id):
    db = Database()
    messagesByConId = """Select * from messages m left join conversations c on m.conversation_id = c.id where c.id = %s;"""
    db.execute(messagesByConId, (conversation_id,))
    messages = db.fetchall() 
    
    return messages

def get_latest_conversation(user_id):
    db = Database()

    # Define the query to get the latest conversation based on message created_at timestamp
    latest_conversation_query = """
        SELECT c.*
        FROM conversations c
        JOIN messages m ON c.id = m.conversation_id
        Where m.sender = %s
        ORDER BY m.created_at DESC
        LIMIT 1;
    """

    db.execute(latest_conversation_query, (user_id,))
    latest_conversation = db.fetchone()

    return latest_conversation

def get_latest_conversation_with_participents(user_id):
    db = Database()
    latest_message_query = """
        SELECT m.*
        FROM messages m
        JOIN users u ON m.sender = u.userid
        Where m.sender = %s
        ORDER BY m.created_at DESC
        LIMIT 1;
    """

    db.execute(latest_message_query, (user_id,))
    latest_message = db.fetchone()
    if latest_message:
        latest_conversation_id = latest_message[7]

        latest_conversation_query = """SELECT * from conversations where id = %s;"""
        db.execute(latest_conversation_query, (latest_conversation_id,))
        latest_conversation = db.fetchone()

        latest_conversation_id, title, created_at = latest_conversation
    
        participants_query = """
                SELECT u.userid, u.name, u.email
                FROM users u
                JOIN conversation_participants cp ON u.userid = cp.user_id
                WHERE cp.conversation_id = %s AND u.userid != %s;
            """
        db.execute(participants_query, (latest_conversation_id, user_id,))

        participants = db.fetchone()

        conversations_and_participants = []

        conversation_info = {
                "conversation_id": latest_conversation_id,
                "title": title,
                "created_at": created_at,
                "participants": [
                    {"receiver_id": participants[0], "receiver_username": participants[1], "receiver_email": participants[2]}
                ]
            }

        conversations_and_participants.append(conversation_info)
        return conversations_and_participants