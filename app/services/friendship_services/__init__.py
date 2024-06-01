from app.db import Database

def saveNewFrinedShip(user_id1, user_id2):
    
    db = Database()

    db.execute("""
        INSERT INTO friendships (user_id1, user_id2, status)
        VALUES (%s, %s, 'pending')
        ON CONFLICT (user_id1, user_id2) DO NOTHING
        RETURNING friendship_id;
    """, (user_id1, user_id2))
    result = db.fetchone()
    db.commit()
    db.close()

    return result

def updateFriendShipStatus(user_id1, user_id2, friendShipStatus):
    print(user_id1, user_id2, friendShipStatus)
    db = Database()
    db.execute("""
        UPDATE friendships
        SET status = %s
        WHERE (user_id1 = %s AND user_id2 = %s) OR (user_id1 = %s AND user_id2 = %s)
    """, (friendShipStatus, user_id1, user_id2, user_id2, user_id1))
    db.commit()
    db.close()

def get_friends(user_id):
    db = Database()

    friends_query = """Select * from users u left outer join friendships f 
    on (u.userid = f.user_id1) or (u.userid = f.user_id2) 
	where f.status = 'accepted' and (f.user_id1 = %s or f.user_id2 = %s) and u.userid <> %s
    """

    db.execute(friends_query, (user_id, user_id, user_id,))
    result  = db.fetchall()
    friends = []
    for friend in result:
        friend = {
            "user_id" : friend[0],
            "name" : friend[1],
            "age": friend[2],
            "email": friend[3],
            "phone": friend[4]
            }
        friends.append(friend)

    return friends