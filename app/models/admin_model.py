from app.models.user_model import User

class Admin(User):
    def __init__(self, userId, name, age, email, phoneNo, password, roleId, token, is_verified):
        super().__init__(userId, name, age, email, phoneNo, password, roleId, token, is_verified)
        # Additional initialization or methods for Admin

    def deleteUser(self, userId):
        super().deleteUser(userId)

    def updateUser(self, userId, **kwargs):
        super().updateUser(userId, **kwargs)