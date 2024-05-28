from db import db_connection


def get_conversations_and_participants(sender_id):
    db = db_connection()
    cursor = db.cursor()
    
    # Subquery to get conversations where the user is the sender
    sender_conversations_query = """
        SELECT DISTINCT c.id, c.title, c.created_at
        FROM conversations c
        JOIN messages m ON c.id = m.conversation_id
        WHERE m.sender_id = %s;
    """
    cursor.execute(sender_conversations_query, (sender_id,))
    sender_conversations = cursor.fetchall()

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
        cursor.execute(participants_query, (conversation_id, sender_id))
        participants = cursor.fetchall()
        
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
    db = db_connection()
    cursor = db.cursor()
 
    messagesByConId = """Select * from messages m left join conversations c on m.conversation_id = c.id where c.id = %s;"""
    cursor.execute(messagesByConId, (conversation_id,))
    messages = cursor.fetchall() 
    
    return messages

def get_latest_conversation(user_id):
    con = db_connection()
    cur = con.cursor()

    # Define the query to get the latest conversation based on message created_at timestamp
    latest_conversation_query = """
        SELECT c.*
        FROM conversations c
        JOIN messages m ON c.id = m.conversation_id
        Where m.sender = %s
        ORDER BY m.created_at DESC
        LIMIT 1;
    """

    cur.execute(latest_conversation_query, (user_id,))
    latest_conversation = cur.fetchone()

    return latest_conversation

def get_latest_conversation_with_participents(user_id):
    con = db_connection()
    cur = con.cursor()

    latest_message_query = """
        SELECT m.*
        FROM messages m
        JOIN users u ON m.sender = u.userid
        Where m.sender = %s
        ORDER BY m.created_at DESC
        LIMIT 1;
    """

    cur.execute(latest_message_query, (user_id,))
    latest_message = cur.fetchone()
    if latest_message:
        latest_conversation_id = latest_message[7]

        latest_conversation_query = """SELECT * from conversations where id = %s;"""
        cur.execute(latest_conversation_query, (latest_conversation_id,))
        latest_conversation = cur.fetchone()

        latest_conversation_id, title, created_at = latest_conversation
    
        participants_query = """
                SELECT u.userid, u.name, u.email
                FROM users u
                JOIN conversation_participants cp ON u.userid = cp.user_id
                WHERE cp.conversation_id = %s AND u.userid != %s;
            """
        cur.execute(participants_query, (latest_conversation_id, user_id,))

        participants = cur.fetchone()

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