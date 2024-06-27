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

    # Получение списка каналов
    async def get_channels(self) -> List[Dict]:
        query = "SELECT channel_id AS id, name FROM channels;"
        rows = await self.conn.fetch(query)
        return [{'channel_id': row['id'], 'name': row['name']} for row in rows]

    # Создание нового канала
    async def create_channel(self, name: str):
        query = "INSERT INTO channels (name) VALUES ($1) RETURNING channel_id;"
        channel_id = await self.conn.fetchval(query, name)
        return channel_id

    # Получение списка работников
    async def get_workers(self) -> List[Dict]:
        query = "SELECT user_id, username FROM users;"
        rows = await self.conn.fetch(query)
        return [{'user_id': row['user_id'], 'username': row['username']} for row in rows]

    # Получение информации о работнике
    async def get_worker_info(self, worker_id: int) -> Dict:
        query = """
        SELECT 
            u.user_id,
            u.username,
            u.role,
            COALESCE(s.tasks_completed, 0) AS tasks_completed,
            COALESCE(s.errors_made, 0) AS errors_made,
            COALESCE(s.amount_spent, 0) AS amount_spent,
            c.name AS channel_name
        FROM users u
        LEFT JOIN statistics s ON u.user_id = s.worker_id
        LEFT JOIN channels c ON u.channel_id = c.channel_id
        WHERE u.user_id = $1;
        """
        return await self.conn.fetchrow(query, worker_id)

    # Получение статистики по каналам
    async def get_statistics_by_channels(self) -> List[Dict]:
        query = """
        SELECT 
            s.*, 
            COALESCE(c.name, 'NULL') AS channel_name
        FROM statistics s
        LEFT JOIN channels c ON s.channel_id = c.channel_id
        WHERE s.channel_id IS NOT NULL;
        """
        rows = await self.conn.fetch(query)
        return rows

    # Получение статистики по работникам
    async def get_statistics_by_workers(self) -> List[Dict]:
        query = """
        SELECT 
            s.*, 
            COALESCE(u.username, 'NULL') AS worker_username
        FROM statistics s
        LEFT JOIN users u ON s.worker_id = u.user_id
        WHERE s.worker_id IS NOT NULL;
        """
        rows = await self.conn.fetch(query)
        return rows

    # Добавление месячного дохода каналу
    async def add_monthly_income_to_channel(self, channel_id: int, amount: float, description: str):
        current_date = datetime.datetime.now()
        query = """
        INSERT INTO finances (channel_id, amount, type, description, created_at)
        VALUES ($1, $2, 'income', $3, $4);
        """
        await self.conn.execute(query, channel_id, amount, description, current_date)

    # Добавление затрат работнику
    async def add_worker_expense(self, worker_id: int, amount: float):
        query = "UPDATE statistics SET amount_spent = amount_spent + $1 WHERE worker_id = $2"
        await self.conn.execute(query, amount, worker_id)

    # Добавление ошибки работнику
    async def add_worker_error(self, worker_id: int, description: str):
        query = "INSERT INTO errors (worker_id, description, created_at) VALUES ($1, $2, $3)"
        await self.conn.execute(query, worker_id, description, datetime.datetime.now())

    # Назначение работника на канал
    async def assign_worker_to_channel(self, worker_id: int, channel_id: int):
        query = """
        UPDATE users
        SET channel_id = $1
        WHERE user_id = $2;
        """
        await self.conn.execute(query, channel_id, worker_id)

    # Создание задачи
    async def create_task(self, channel_id: int, title: str, description: str):
        query = """
        INSERT INTO tasks (channel_id, title, description, created_at)
        VALUES ($1, $2, $3, $4)
        RETURNING task_id;
        """
        task_id = await self.conn.fetchval(query, channel_id, title, description, datetime.datetime.now())
        return task_id

    # Получение списка задач
    async def get_tasks(self) -> List[Dict]:
        query = "SELECT task_id, title FROM tasks;"
        rows = await self.conn.fetch(query)
        return [{'id': row['task_id'], 'title': row['title']} for row in rows]

    # Получение деталей задачи
    async def get_task_details(self, task_id: int) -> Dict:
        query = "SELECT * FROM tasks WHERE task_id = $1;"
        row = await self.conn.fetchrow(query, task_id)
        return {'details': row['description'], 'title': row['title']}

    # Обновление статуса задачи
    async def update_task_status(self, task_id: int, status: str):
        query = """
        UPDATE tasks
        SET status = $2, updated_at = $3
        WHERE task_id = $1;
        """
        await self.conn.execute(query, task_id, status, datetime.datetime.now())

    # Получение общей статистики
    async def get_overall_statistics(self) -> Dict:
        query = """
        SELECT 
            SUM(income) AS total_income,
            SUM(expense) AS total_expense,
            SUM(income - expense) AS total_net_profit,
            SUM(tasks_completed) AS total_tasks_completed
        FROM statistics;
        """
        row = await self.conn.fetchrow(query)
        return dict(row)

    # Добавление ошибки (для задачи и работника)
    async def add_error(self, task_id: int, worker_id: int, description: str):
        query = """
        INSERT INTO errors (task_id, worker_id, description)
        VALUES ($1, $2, $3);
        """
        await self.conn.execute(query, task_id, worker_id, description)

    # Обновление финансовых данных
    async def update_finances(self, channel_id: int, amount: float, type: str, description: str):
        query = """
        INSERT INTO finances (channel_id, amount, type, description)
        VALUES ($1, $2, $3, $4);
        """
        await self.conn.execute(query, channel_id, amount, type, description)

    # Получение статистики по каналу или работнику
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

    # Получение задач для ревью (модератор)
    async def get_tasks_for_review(self) -> List[Dict]:
        query = "SELECT task_id, title FROM tasks WHERE status = 'pending_review';"
        rows = await self.conn.fetch(query)
        return [{'id': row['task_id'], 'title': row['title']} for row in rows]

    # Создание истории (модератор)
    async def create_story(self, story_details: str):
        query = "INSERT INTO tasks (description) VALUES ($1) RETURNING task_id;"  # Assuming story details go into tasks table
        story_id = await self.conn.fetchval(query, story_details)
        return story_id

    # Получение задач по preview maker
    async def get_tasks_by_preview_maker(self, preview_maker_id: int) -> List[Dict]:
        query = "SELECT task_id, title FROM tasks WHERE assigned_to = $1 AND status = 'assigned';"
        rows = await self.conn.fetch(query, preview_maker_id)
        return [{'id': row['task_id'], 'title': row['title']} for row in rows]

    # Назначение задачи preview maker
    async def assign_task_to_preview_maker(self, task_id: int, preview_maker_id: int):
        query = "UPDATE tasks SET assigned_to = $1 WHERE task_id = $2;"
        await self.conn.execute(query, preview_maker_id, task_id)

    # Получение задач по shooter
    async def get_tasks_by_shooter(self, shooter_id: int) -> List[Dict]:
        query = "SELECT task_id, title FROM tasks WHERE assigned_to = $1 AND status = 'assigned';"
        rows = await self.conn.fetch(query, shooter_id)
        return [{'id': row['task_id'], 'title': row['title']} for row in rows]

    # Назначение задачи shooter
    async def assign_task_to_shooter(self, task_id: int, shooter_id: int):
        query = "UPDATE tasks SET assigned_to = $1 WHERE task_id = $2;"
        await self.conn.execute(query, shooter_id, task_id)

    # Получение задач по editor
    async def get_tasks_by_editor(self, editor_id: int) -> List[Dict]:
        query = "SELECT task_id, title FROM tasks WHERE assigned_to = $1 AND status = 'assigned';"
        rows = await self.conn.fetch(query, editor_id)
        return [{'id': row['task_id'], 'title': row['title']} for row in rows]

    # Назначение задачи editor
    async def assign_task_to_editor(self, task_id: int, editor_id: int):
        query = "UPDATE tasks SET assigned_to = $1 WHERE task_id = $2;"
        await self.conn.execute(query, editor_id, task_id)

    # Обновление статуса задачи (универсальный метод)
    async def update_task_status(self, task_id: int, status: str):
        query = "UPDATE tasks SET status = $2, updated_at = $3 WHERE task_id = $1;"
        await self.conn.execute(query, task_id, status, datetime.datetime.now())

    # Получение пользователя по username
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

# Получение списка работников для указанного канала
async def get_workers_by_channel(self, channel_id: int) -> List[Dict]:
    query = """
    SELECT u.user_id, u.username
    FROM users u
    LEFT JOIN channels c ON u.channel_id = c.channel_id
    WHERE u.channel_id = $1;
    """
    rows = await self.conn.fetch(query, channel_id)
    return [{'user_id': row['user_id'], 'username': row['username']} for row in rows]