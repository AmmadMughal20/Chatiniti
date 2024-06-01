import secrets
from app.db import Database
from flask import flash, redirect, url_for
from app.utils import sendVerificationEmail

def getUserByToken(token):
    db = Database()
    db.execute("SELECT * FROM USERS WHERE token = %s", (token,))
    user = db.fetchone()
    db.close()
    return user

def updateUserToTokenVerified(userId):
    db = Database()
    db.execute("UPDATE USERS SET is_verified = TRUE WHERE userId = %s", (userId,))
    db.commit()
    db.close()

def createUser(userId, name, age, email, phoneNo, password, role):
    token = secrets.token_urlsafe(16)
    sendVerificationEmail(email, token)
    flash('An email has been sent to verify your account.')  # Flash message here
    db = Database()
    insertBookSqlQuery = """INSERT INTO USERS (userId, name, age, email, phone, password, roleId, token) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"""
    db.execute(insertBookSqlQuery,
                    (
                        userId,
                        name,
                        age,
                        email,
                        phoneNo,
                        password,
                        role,
                        token
                    )
                )
    db.commit()
    db.close()
    return redirect(url_for('authentication.signIn'))

def getUserById(user_Id):
    db = Database()
    get_user_query = """Select * from users where userid = %s;"""
    db.execute(get_user_query, (user_Id,))
    user = db.fetchone()
    db.close()
    return user

def updateToken(user_id, token):
    db = Database()
    db.execute("UPDATE USERS SET token = %s WHERE userId = %s", (token, user_id))
    db.commit() 
    db.close()

def getAllUsers(logged_in_user_id):
    db = Database()
    allUsersQry = """
                SELECT u.userid, u.name, u.age, u.email, u.phone,
                       f.status, 
                       CASE
                           WHEN f.user_id1 = %s THEN 'requested'
                           WHEN f.user_id2 = %s THEN 'received'
                           ELSE 'none'
                       END AS friendship_direction
                FROM users u
                LEFT JOIN friendships f ON
                    (u.userid = f.user_id1 AND f.user_id2 = %s)
                    OR (u.userid = f.user_id2 AND f.user_id1 = %s)
            """
    db.execute(allUsersQry, (logged_in_user_id, logged_in_user_id, logged_in_user_id, logged_in_user_id))
    usersArray = db.fetchall()
    return usersArray

    