from db import db_connection


def get_friends(user_id):
    print(user_id, 'user_id')
    con = db_connection()
    curr = con.cursor()

    friends_query = """Select * from users u left outer join friendships f 
    on (u.userid = f.user_id1) or (u.userid = f.user_id2) 
	where f.status = 'accepted' and (f.user_id1 = %s or f.user_id2 = %s) and u.userid <> %s
    """

    curr.execute(friends_query, (user_id, user_id, user_id,))
    result  = curr.fetchall()
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