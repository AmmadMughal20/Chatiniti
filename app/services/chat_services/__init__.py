from app.db import Database


def get_conversations_and_participants(sender_id):
    db = Database()
    # Subquery to get conversations where the user is the sender
    sender_conversations_query = """
        SELECT DISTINCT c.id, c.title, c.created_at
        FROM conversations c
        JOIN messages m ON c.id = m.conversation_id
        WHERE m.sender_id = %s;
    """
    db.execute(sender_conversations_query, (sender_id,))
    sender_conversations = db.fetchall()

    # Main query to get receivers in each conversation excluding the sender
    conversations_and_participants = []
    for conversation in sender_conversations:
        conversation_id, title, created_at = conversation
        participants_query = """
            SELECT u.userid, u.name, u.email
            FROM users u
            JOIN conversation_participants cp ON u.userid = cp.user_id
            WHERE cp.conversation_id = %s AND u.userid != %s;
        """
        db.execute(participants_query, (conversation_id, sender_id))
        participants = db.fetchall()
        
        conversation_info = {
            "conversation_id": conversation_id,
            "title": title,
            "created_at": created_at,
            "participants": [
                {"receiver_id": p[0], "receiver_username": p[1], "receiver_email": p[2]}
                for p in participants
            ]
        }
        conversations_and_participants.append(conversation_info)

    return conversations_and_participants

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