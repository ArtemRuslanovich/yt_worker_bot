from database import repository

class Authenticator:
    def __init__(self):
        pass

    def authenticate_user(self, username, password, role):
        user = repository.DatabaseRepository.get_user_by_username(username)

        if user is None:
            return False, 'Пассажир не найден'

        if user.password != password:
            return False, 'Неправильный пароль)'

        if user.role.name != role:
            return False, 'Неправильная роль'

        return True, 'Авторизован'

    def check_role(self, user, role):
        if user.role.name == role:
            return True
        else:
            return False