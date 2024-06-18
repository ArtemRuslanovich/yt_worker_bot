from database.database import Database


def authenticate(username, password, role):
    # Проверка пользователя в базе данных
    user = Database.get_user_by_username(username)
    if not user or user.password != password or user.role != role:
        return False
    return True