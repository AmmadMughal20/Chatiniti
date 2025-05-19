import re
import secrets
from abc import ABC
from werkzeug.security import generate_password_hash, check_password_hash
from app.authentication.authentication_validations import validate_password
from app.db import Database
from app.utils import sendVerificationEmail

class User(ABC):

    def __init__(self, userId, name, age, email, phoneNo, password, roleId, token, is_verified, is_online):
        self.userId = userId
        self.name = name
        self.age = age
        self.email = email
        self.phoneNo = phoneNo
        self.password = password
        self.roleId = roleId
        self.token = token
        self.is_verified = is_verified
        self.is_online = is_online

    @classmethod
    def signIn(cls, user_id, password):
        db = Database()
        query = """SELECT * FROM USERS WHERE userId=%s"""
        db.execute(query, (user_id,))
        user_data = db.fetchone()
        db.close()
        if user_data and check_password_hash(user_data[5], password):  # Assuming password is the 6th field
            return cls(*user_data)
        return None

    @classmethod
    def createUser(cls, userId, name, age, email, phoneNo, password, roleId):
        token = secrets.token_urlsafe(16)
        hashed_password = generate_password_hash(password)
        sendVerificationEmail(email, token)
        db = Database()
        insertUserQuery = """INSERT INTO USERS (userId, name, age, email, phone, password, roleId, token) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"""
        db.execute(insertUserQuery,
                    (
                        userId,
                        name,
                        age,
                        email,
                        phoneNo,
                        hashed_password,
                        roleId,
                        token
                    )
                )
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

    @classmethod
    def getUserById(cls, user_Id):
        db = Database()
        getUserQuery = """SELECT * FROM users WHERE userid = %s"""
        db.execute(getUserQuery, (user_Id,))
        user_data = db.fetchone()
        db.close()
        if user_data:
            return cls(*user_data)
        return None

    @classmethod
    def getUserByEmail(cls, email):
        db = Database()
        userByEmailQuery = "Select * from users where email = %s"
        db.execute(userByEmailQuery, (email,))
        user_data = db.fetchone()
        db.close()
        if user_data:
            return User(*user_data)
        else:
            return None

    @classmethod
    def getUserByPhone(cls, phone):
        db = Database()
        getUserByPhoneQuery = "Select * from users where phone = %s"
        db.execute(getUserByPhoneQuery, (phone,))
        user_data = db.fetchone()
        db.close()
        if user_data:
            return User(*user_data)
        else:
            return None
        
    @classmethod
    def updateToken(cls, user_id, token):
        db = Database()
        db.execute("UPDATE USERS SET token = %s WHERE userId = %s", (token, user_id))
        db.commit()
        db.close()

    @classmethod
    def getUserByToken(cls, token):
        db = Database()
        db.execute("SELECT * FROM USERS WHERE token = %s", (token,))
        user_data = db.fetchone()
        db.close()
        if user_data:
            return cls(*user_data)
        return None

    def updateUserToTokenVerified(self):
        db = Database()
        db.execute("UPDATE USERS SET is_verified = TRUE WHERE userId = %s", (self.userId,))
        db.commit()
        db.close()

    @classmethod
    def update_password_by_token(cls, token, password):
        user = cls.getUserByToken(token)
        if user:
            hashed_password = generate_password_hash(password)
            db = Database()
            query = """UPDATE USERS SET password = %s WHERE token = %s"""
            db.execute(query, (hashed_password, token))
            db.commit()
            db.close()

    @staticmethod
    def validate_email(email):
        pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        return re.match(pattern, email) is not None

    @staticmethod
    def deleteUser(userId):
        db = Database()
        delete_user_query = "DELETE FROM USERS WHERE userId = %s"
        db.execute(delete_user_query, (userId,))
        db.commit()
        db.close()

    @staticmethod
    def updateUser(userId, **kwargs):
        db = Database()
        columns = ', '.join(f"{k} = %s" for k in kwargs.keys())
        values = list(kwargs.values()) + [userId]
        update_user_query = f"UPDATE USERS SET {columns} WHERE userId = %s"
        db.execute(update_user_query, values)
        db.commit()
        db.close()
