import re
import secrets

from app.authentication.authentication_validations import validate_password
from app.db import Database
from app.utils import sendVerificationEmail

class User:
    def __init__(self, userId, name,age, email, phoneNo, password, roleId, token, is_verified):
        self.userId = userId
        self.name = name
        self.age = age
        self.email = email
        self.phoneNo = phoneNo
        self.password = password
        self.roleId = roleId
        self.token = token
        self.is_verified = is_verified
        
    @staticmethod
    def signIn(user_id, password):
        db = Database()
        query = """SELECT * FROM USERS WHERE userId=%s AND password=%s"""
        db.execute(query, (user_id, password))
        user = db.fetchone()
        db.close()
        if user:
            return User(*user)
        return None
    
    @staticmethod
    def createUser(userId, name, age, email, phoneNo, password, roleId):
        token = secrets.token_urlsafe(16)
        sendVerificationEmail(email, token)
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
                            roleId,
                            token
                        )
                    )
        db.commit()
        db.close()

    @staticmethod
    def getUserById(user_Id):
        db = Database()
        get_user_query = """Select * from users where userid = %s;"""
        db.execute(get_user_query, (user_Id,))
        user = db.fetchone()
        db.close()
        if user:
            return User(*user)
        return None

    def updateToken(self, token):
        db = Database()
        db.execute("UPDATE USERS SET token = %s WHERE userId = %s", (token, self.userId))
        db.commit() 
        db.close()
        
    @staticmethod
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

    @staticmethod
    def getUserByToken(token):
        db = Database()
        db.execute("SELECT userid, name, age, email, phone, password, roleid, token FROM USERS WHERE token = %s", (token,))
        user = db.fetchone()
        db.close()
        return user

    def updateUserToTokenVerified(self):
        db = Database()
        db.execute("UPDATE USERS SET is_verified = TRUE WHERE userId = %s", (self.userId,))
        db.commit()
        db.close()

    @staticmethod
    def update_password_by_token(token, password):
            user = User.getUserByToken(token)
            if user:
                db = Database()
                query = """UPDATE USERS SET password = %s WHERE token = %s"""
                db.execute(query, (password, token))
                db.commit()
                db.close()
    
    @staticmethod
    def validate_email(email):
        # Basic email validation using regular expression
        # You can customize the regex pattern according to your requirements
        pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        return re.match(pattern, email) is not None
