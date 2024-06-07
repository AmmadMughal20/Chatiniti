from app.models.user_model import User


class RegularUser(User):
    def __init__(self, userId, name, age, email, phoneNo, password, roleId, token, is_verified):
        super().__init__(userId, name, age, email, phoneNo, password, roleId, token, is_verified)
        # Additional initialization or methods for RegularUser
