
from database.database import Database


async def authenticate(db: Database, username: str, password: str, role: str) -> bool:
    print(f"Fetching user {username} from database")  # Debugging line
    try:
        user = await db.get_user_by_username(username)
        if user and user['password'] == password and user['role'] == role:
            return True
    except Exception as e:
        print(f"Error in authenticate function: {e}")
    return False