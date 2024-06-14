from database import repository


class Authenticator:
    def __init__(self, db_repository: repository.DatabaseRepository):
        self.db_repository = db_repository

    def authenticate_user(self, username, password, role):
        user = self.db_repository.get_user_by_username(username)

        if user is None:
            return False, 'Пользователь не найден'

        if user.password != password:
            return False, 'Неправильный пароль'

        if user.role.name != role:
            return False, 'Неправильная роль'

        return True, 'Авторизован'
#
    def check_role(self, user, role):
        if user.role.name == role:
            return True
        else:
            return False
