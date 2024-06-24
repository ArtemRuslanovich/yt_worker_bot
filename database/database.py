import datetime
import asyncpg
from typing import List, Dict

class Database:
    def __init__(self, dsn: str):
        self.dsn = dsn
        self.conn = None

    async def connect(self):
        self.conn = await asyncpg.connect(self.dsn)
        print("Database connection established.")

    async def close(self):
        await self.conn.close()
        print("Database connection closed.")

    # manager

    async def get_channels(self) -> List[Dict]:
        query = "SELECT * FROM channels;"
        rows = await self.conn.fetch(query)
        return [{'id': row['channel_id'], 'name': row['name']} for row in rows]

    async def create_task(self, channel_id: int, title: str, description: str):
        query = """
        INSERT INTO tasks (channel_id, title, description)
        VALUES ($1, $2, $3)
        RETURNING task_id;
        """
        task_id = await self.conn.fetchval(query, channel_id, title, description)
        return task_id

    async def get_tasks(self) -> List[Dict]:
        query = "SELECT * FROM tasks;"
        rows = await self.conn.fetch(query)
        return [{'id': row['task_id'], 'title': row['title']} for row in rows]

    async def get_task_details(self, task_id: int) -> Dict:
        query = "SELECT * FROM tasks WHERE task_id = $1;"
        row = await self.conn.fetchrow(query, task_id)
        return {'details': row['description'], 'title': row['title']}

    async def update_task_status(self, task_id: int, status: str):
        query = """
        UPDATE tasks
        SET status = $2
        WHERE task_id = $1;
        """
        await self.conn.execute(query, task_id, status)

    # Методы для обработки других таблиц (например, ошибок, доходов и расходов)
    async def add_error(self, task_id: int, worker_id: int, description: str):
        query = """
        INSERT INTO errors (task_id, worker_id, description)
        VALUES ($1, $2, $3);
        """
        await self.conn.execute(query, task_id, worker_id, description)

    async def update_finances(self, channel_id: int, amount: float, type: str, description: str):
        query = """
        INSERT INTO finances (channel_id, amount, type, description)
        VALUES ($1, $2, $3, $4);
        """
        await self.conn.execute(query, channel_id, amount, type, description)

    async def get_statistics(self, channel_id: int = None, worker_id: int = None) -> Dict:
        if channel_id:
            query = "SELECT * FROM statistics WHERE channel_id = $1;"
            row = await self.conn.fetchrow(query, channel_id)
        elif worker_id:
            query = "SELECT * FROM statistics WHERE worker_id = $1;"
            row = await self.conn.fetchrow(query, worker_id)
        else:
            query = "SELECT * FROM statistics;"
            row = await self.conn.fetch(query)
        return row
    
    #admin

    async def create_channel(self, name: str):
        query = "INSERT INTO channels (name) VALUES ($1) RETURNING channel_id;"
        channel_id = await self.conn.fetchval(query, name)
        return channel_id

    async def get_workers(self):
        query = "SELECT * FROM users;"
        rows = await self.conn.fetch(query)
        return [{'user_id': row['user_id'], 'username': row['username']} for row in rows]

    async def get_statistics_by_channels(self):
        query = """
        SELECT 
            statistics.*,
            channels.name AS channel_name,
            users.username AS worker_username
        FROM statistics
        JOIN channels ON statistics.channel_id = channels.channel_id
        LEFT JOIN users ON statistics.worker_id = users.user_id
        WHERE statistics.channel_id IS NOT NULL;
        """
        try:
            rows = await self.conn.fetch(query)
            return rows
        except Exception as e:
            print(f"Error fetching statistics by channels: {e}")
            return []

    async def get_statistics_by_workers(self):
        query = """
        SELECT 
            statistics.*,
            users.username AS worker_username
        FROM statistics
        JOIN users ON statistics.worker_id = users.user_id
        WHERE statistics.worker_id IS NOT NULL;
        """
        try:
            rows = await self.conn.fetch(query)
            return rows
        except Exception as e:
            print(f"Error fetching statistics by workers: {e}")
            return []

    async def get_overall_statistics(self):
        query = """
        SELECT 
            SUM(income) AS total_income,
            SUM(expense) AS total_expense,
            SUM(income - expense) AS total_net_profit,
            SUM(tasks_completed) AS total_tasks_completed
        FROM statistics;
        """
        rows = await self.conn.fetch(query)
        return rows
    
    async def add_monthly_income_to_channel(self, channel_id: int, amount: float, description: str):
        current_month = datetime.now().strftime("%Y-%m")
        query = """
        INSERT INTO finances (channel_id, amount, type, description, created_at)
        VALUES ($1, $2, 'income', $3, $4);
        """
        await self.conn.execute(query, channel_id, amount, description, current_month)


    # moderator

    async def create_story(self, story_details: str):
        query = "INSERT INTO stories (details) VALUES ($1) RETURNING story_id;"
        story_id = await self.conn.fetchval(query, story_details)
        return story_id

    async def get_tasks_for_review(self):
        query = "SELECT * FROM tasks WHERE status = 'pending_review';"
        rows = await self.conn.fetch(query)
        return [{'id': row['task_id'], 'title': row['title']} for row in rows]

    async def get_task_details(self, task_id: int):
        query = "SELECT * FROM tasks WHERE task_id = $1;"
        row = await self.conn.fetchrow(query, task_id)
        return {'details': row['description'], 'title': row['title']}
    
    # preview_maker

    async def get_tasks_by_preview_maker(self, preview_maker_id: int):
        query = "SELECT * FROM tasks WHERE assigned_to = $1 AND status = 'assigned';"
        rows = await self.conn.fetch(query, preview_maker_id)
        return [{'id': row['task_id'], 'title': row['title']} for row in rows]

    async def assign_task_to_preview_maker(self, task_id: int, preview_maker_id: int):
        query = "UPDATE tasks SET assigned_to = $1 WHERE task_id = $2;"
        await self.conn.execute(query, preview_maker_id, task_id)

    async def update_task_status(self, task_id: int, status: str):
        query = "UPDATE tasks SET status = $2 WHERE task_id = $1;"
        await self.conn.execute(query, task_id, status)

    #shooter
    async def get_tasks_by_shooter(self, shooter_id: int):
        query = "SELECT * FROM tasks WHERE assigned_to = $1 AND status = 'assigned';"
        rows = await self.conn.fetch(query, shooter_id)
        return [{'id': row['task_id'], 'title': row['title']} for row in rows]

    async def assign_task_to_shooter(self, task_id: int, shooter_id: int):
        query = "UPDATE tasks SET assigned_to = $1 WHERE task_id = $2;"
        await self.conn.execute(query, shooter_id, task_id)

    async def update_task_status(self, task_id: int, status: str):
        query = "UPDATE tasks SET status = $2 WHERE task_id = $1;"
        await self.conn.execute(query, task_id, status)

    #editor 
    async def get_tasks_by_editor(self, editor_id: int):
        query = "SELECT * FROM tasks WHERE assigned_to = $1 AND status = 'assigned';"
        rows = await self.conn.fetch(query, editor_id)
        return [{'id': row['task_id'], 'title': row['title']} for row in rows]

    async def assign_task_to_editor(self, task_id: int, editor_id: int):
        query = "UPDATE tasks SET assigned_to = $1 WHERE task_id = $2;"
        await self.conn.execute(query, editor_id, task_id)

    async def update_task_status(self, task_id: int, status: str):
        query = "UPDATE tasks SET status = $2 WHERE task_id = $1;"
        await self.conn.execute(query, task_id, status)

    #auth_service
        
    async def get_user_by_username(self, username: str) -> Dict:
        query = """
        SELECT user_id, username, password, role 
        FROM users 
        WHERE username = $1;
        """
        try:
            user = await self.conn.fetchrow(query, username)
            if user:
                return {
                    'user_id': user['user_id'],
                    'username': user['username'],
                    'password': user['password'],
                    'role': user['role']
                }
        except Exception as e:
            print(f"Error fetching user by username: {e}")
        return None