
from database.database import Database


async def authenticate(db, username: str, password: str, role: str):
    query = """
    SELECT user_id, role FROM users WHERE username = $1 AND password = $2 AND role = $3;
    """
    row = await db.conn.fetchrow(query, username, password, role)
    if row:
        return {'user_id': row['user_id'], 'role': row['role']}
    return None