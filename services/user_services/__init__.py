from db import db_connection


def getUserById(user_Id):
    con = db_connection()
    cur = con.cursor()

    get_user_query = """Select * from users where userid = %s;"""

    cur.execute(get_user_query, (user_Id,))
    user = cur.fetchone()
    return user
    