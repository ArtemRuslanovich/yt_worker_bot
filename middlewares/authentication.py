from database import repository

class Authenticator:
    def __init__(self):
        pass

    def authenticate_user(self, username, password, role):
        user = repository.get_user_by_username(username)

        if user is None:
            return False, 'User not found'

        if user.password != password:
            return False, 'Incorrect password'

        if user.role.name != role:
            return False, 'Incorrect role'

        return True, 'Authentication successful'

    def check_role(self, user, role):
        if user.role.name == role:
            return True
        else:
            return False