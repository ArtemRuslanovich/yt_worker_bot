from datetime import datetime
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

    async def get_channels(self) -> List[Dict]:
        query = "SELECT channel_id AS id, name FROM channels;"
        rows = await self.conn.fetch(query)
        return [{'channel_id': row['id'], 'name': row['name']} for row in rows]

    async def create_channel(self, name: str):
        query = "INSERT INTO channels (name) VALUES ($1) RETURNING channel_id;"
        channel_id = await self.conn.fetchval(query, name)
        return channel_id

    async def get_workers(self) -> List[Dict]:
        query = "SELECT user_id, username FROM users;"
        rows = await self.conn.fetch(query)
        return [{'user_id': row['user_id'], 'username': row['username']} for row in rows]

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
        row = await self.conn.fetchrow(query, worker_id)
        return row

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

    async def add_monthly_income_to_channel(self, channel_id: int, amount: float, description: str):
        current_date = datetime.now()
        query = """
        INSERT INTO finances (channel_id, amount, type, description, created_at)
        VALUES ($1, $2, 'income', $3, $4);
        """
        await self.conn.execute(query, channel_id, amount, description, current_date)

    async def add_worker_expense(self, worker_id: int, amount: float):
        query = "UPDATE statistics SET amount_spent = amount_spent + $1 WHERE worker_id = $2"
        await self.conn.execute(query, amount, worker_id)

    async def add_worker_error(self, worker_id: int, description: str):
        query = "INSERT INTO errors (worker_id, description, created_at) VALUES ($1, $2, $3)"
        await self.conn.execute(query, worker_id, description, datetime.now())

        # Обновление общей статистики
        update_statistics_query = """
        UPDATE statistics
        SET errors_made = errors_made + 1
        WHERE worker_id = $1
        """
        await self.conn.execute(update_statistics_query, worker_id)

        # Обновление месячной статистики
        current_month = datetime.now().month
        current_year = datetime.now().year
        update_monthly_statistics_query = """
        INSERT INTO monthly_statistics (worker_id, date, errors_made, tasks_completed)
        VALUES ($1, $2, 1, 0)
        ON CONFLICT (worker_id, date) DO UPDATE
        SET errors_made = monthly_statistics.errors_made + 1
        """
        await self.conn.execute(update_monthly_statistics_query, worker_id, datetime.now().replace(day=1))

    async def assign_worker_to_channel(self, worker_id: int, channel_id: int):
        query = """
        UPDATE users
        SET channel_id = $1
        WHERE user_id = $2;
        """
        await self.conn.execute(query, channel_id, worker_id)

    async def create_task(self, channel_id: int, title: str, description: str, assigned_to: int, status: str) -> int:
        query = """
        INSERT INTO tasks (channel_id, title, description, assigned_to, status, created_at)
        VALUES ($1, $2, $3, $4, $5, $6) RETURNING task_id;
        """
        task_id = await self.conn.fetchval(query, channel_id, title, description, assigned_to, status, datetime.now())
        return task_id

    async def get_tasks(self) -> List[Dict]:
        query = "SELECT task_id, title FROM tasks;"
        rows = await self.conn.fetch(query)
        return [{'id': row['task_id'], 'title': row['title']} for row in rows]

    async def get_task_details(self, task_id: int) -> Dict:
        query = """
        SELECT 
            t.title, 
            t.description, 
            t.file_or_link, 
            t.assigned_to, 
            t.revision_message, 
            u.username AS worker_name, 
            c.name AS channel_name
        FROM tasks t
        LEFT JOIN users u ON t.assigned_to = u.user_id
        LEFT JOIN channels c ON t.channel_id = c.channel_id
        WHERE t.task_id = $1;
        """
        row = await self.conn.fetchrow(query, task_id)
        if not row:
            return {}
        return {
            'title': row['title'],
            'description': row['description'],
            'file_or_link': row['file_or_link'],
            'assigned_to': row['assigned_to'],
            'revision_message': row['revision_message'],
            'worker_name': row['worker_name'],
            'channel_name': row['channel_name']
        }

    async def update_task_status(self, task_id: int, status: str):
        query = """
        UPDATE tasks
        SET status = $2, updated_at = $3
        WHERE task_id = $1;
        """
        await self.conn.execute(query, task_id, status, datetime.now())

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

    async def add_error(self, task_id: int, assigned_to: int, description: str):
        query = """
        INSERT INTO errors (task_id, worker_id, description, created_at)
        VALUES ($1, $2, $3, $4);
        """
        await self.conn.execute(query, task_id, assigned_to, description, datetime.now())

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

    async def get_tasks_for_review(self) -> List[Dict]:
        query = "SELECT task_id, title FROM tasks WHERE status = 'pending_review';"
        rows = await self.conn.fetch(query)
        return [{'id': row['task_id'], 'title': row['title']} for row in rows]

    async def get_tasks_by_preview_maker(self, preview_maker_id: int) -> List[Dict]:
        query = """
        SELECT task_id, title 
        FROM tasks 
        WHERE assigned_to = $1 AND (status = 'assigned' OR status = 'needs_revision');
        """
        rows = await self.conn.fetch(query, preview_maker_id)
        return [{'id': row['task_id'], 'title': row['title']} for row in rows]

    async def assign_task_to_preview_maker(self, task_id: int, preview_maker_id: int):
        query = "UPDATE tasks SET assigned_to = $1 WHERE task_id = $2;"
        await self.conn.execute(query, preview_maker_id, task_id)

    async def get_tasks_by_shooter(self, shooter_id: int) -> List[Dict]:
        query = """
        SELECT task_id, title 
        FROM tasks 
        WHERE assigned_to = $1 AND (status = 'assigned' OR status = 'needs_revision');
        """
        rows = await self.conn.fetch(query, shooter_id)
        return [{'id': row['task_id'], 'title': row['title']} for row in rows]

    async def assign_task_to_shooter(self, task_id: int, shooter_id: int):
        query = "UPDATE tasks SET assigned_to = $1 WHERE task_id = $2;"
        await self.conn.execute(query, shooter_id, task_id)

    async def get_tasks_by_editor(self, editor_id: int) -> List[Dict]:
        query = """
        SELECT task_id, title 
        FROM tasks 
        WHERE assigned_to = $1 AND (status = 'assigned' OR status = 'needs_revision');
        """
        rows = await self.conn.fetch(query, editor_id)
        return [{'id': row['task_id'], 'title': row['title']} for row in rows]

    async def assign_task_to_editor(self, task_id: int, editor_id: int):
        query = "UPDATE tasks SET assigned_to = $1 WHERE task_id = $2;"
        await self.conn.execute(query, editor_id, task_id)

    async def update_task_status(self, task_id: int, status: str):
        query = "UPDATE tasks SET status = $2, updated_at = $3 WHERE task_id = $1;"
        await self.conn.execute(query, task_id, status, datetime.now())

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

    async def get_workers_by_channel(self, channel_id: int) -> List[Dict]:
        query = """
        SELECT u.user_id, u.username
        FROM users u
        LEFT JOIN channels c ON u.channel_id = c.channel_id
        WHERE u.channel_id = $1;
        """
        rows = await self.conn.fetch(query, channel_id)
        return [{'user_id': row['user_id'], 'username': row['username']} for row in rows]

    async def get_tasks_by_editor(self, editor_id: int) -> List[Dict]:
        query = "SELECT task_id, title FROM tasks WHERE assigned_to = $1 AND status = 'assigned';"
        rows = await self.conn.fetch(query, editor_id)
        return [{'id': row['task_id'], 'title': row['title']} for row in rows]

    async def assign_task_to_editor(self, task_id: int, editor_id: int):
        query = "UPDATE tasks SET assigned_to = $1 WHERE task_id = $2;"
        await self.conn.execute(query, editor_id, task_id)

    async def get_tasks_by_preview_maker(self, preview_maker_id: int) -> List[Dict]:
        query = "SELECT task_id, title FROM tasks WHERE assigned_to = $1 AND status = 'assigned';"
        rows = await self.conn.fetch(query, preview_maker_id)
        return [{'id': row['task_id'], 'title': row['title']} for row in rows]

    async def assign_task_to_preview_maker(self, task_id: int, preview_maker_id: int):
        query = "UPDATE tasks SET assigned_to = $1 WHERE task_id = $2;"
        await self.conn.execute(query, preview_maker_id, task_id)

    async def get_tasks_by_shooter(self, shooter_id: int) -> List[Dict]:
        query = "SELECT task_id, title FROM tasks WHERE assigned_to = $1 AND status = 'assigned';"
        rows = await self.conn.fetch(query, shooter_id)
        return [{'id': row['task_id'], 'title': row['title']} for row in rows]

    async def assign_task_to_shooter(self, task_id: int, shooter_id: int):
        query = "UPDATE tasks SET assigned_to = $1 WHERE task_id = $2;"
        await self.conn.execute(query, shooter_id, task_id)

    async def get_tasks_for_review(self) -> List[Dict]:
        query = "SELECT task_id, title FROM tasks WHERE status = 'pending_review';"
        rows = await self.conn.fetch(query)
        return [{'id': row['task_id'], 'title': row['title']} for row in rows]

    async def update_task_link(self, task_id: int, file_or_link: str):
        query = "UPDATE tasks SET file_or_link = $1 WHERE task_id = $2;"
        await self.conn.execute(query, file_or_link, task_id)

    async def reset_monthly_errors(self):
        query = "UPDATE statistics SET errors_made = 0;"
        await self.conn.execute(query)

    async def get_worker_monthly_info(self, worker_id: int) -> Dict:
        current_month = datetime.now().month
        current_year = datetime.now().year

        query = """
        SELECT 
            u.user_id,
            u.username,
            u.role,
            COALESCE(s.tasks_completed, 0) AS tasks_completed,
            COALESCE(s.errors_made, 0) AS errors_made,
            COALESCE(s.amount_spent, 0) AS amount_spent,
            COALESCE(m.tasks_completed, 0) AS monthly_tasks_completed,
            COALESCE(m.errors_made, 0) AS monthly_errors_made,
            c.name AS channel_name
        FROM users u
        LEFT JOIN statistics s ON u.user_id = s.worker_id
        LEFT JOIN (
            SELECT
                worker_id,
                SUM(tasks_completed) AS tasks_completed,
                SUM(errors_made) AS errors_made
            FROM monthly_statistics
            WHERE EXTRACT(MONTH FROM date) = $1 AND EXTRACT(YEAR FROM date) = $2
            GROUP BY worker_id
        ) m ON u.user_id = m.worker_id
        LEFT JOIN channels c ON u.channel_id = c.channel_id
        WHERE u.user_id = $3;
        """
        return await self.conn.fetchrow(query, current_month, current_year, worker_id)

    async def update_task_completion(self, worker_id: int):
        # Обновление общей статистики
        update_statistics_query = """
        UPDATE statistics
        SET tasks_completed = tasks_completed + 1
        WHERE worker_id = $1
        """
        await self.conn.execute(update_statistics_query, worker_id)

        # Обновление месячной статистики
        current_month = datetime.now().month
        current_year = datetime.now().year
        update_monthly_statistics_query = """
        INSERT INTO monthly_statistics (worker_id, date, tasks_completed, errors_made)
        VALUES ($1, $2, 1, 0)
        ON CONFLICT (worker_id, date) DO UPDATE
        SET tasks_completed = monthly_statistics.tasks_completed + 1
        """
        await self.conn.execute(update_monthly_statistics_query, worker_id, datetime.now().replace(day=1))


    # Создание сценария
    async def create_story(self, story_details: str):
        query = "INSERT INTO stories (description, created_at) VALUES ($1, $2) RETURNING story_id;"
        story_id = await self.conn.fetchval(query, story_details, datetime.now())
        return story_id
    
    # Получение списка сценариев
    async def get_stories(self) -> List[Dict]:
        query = "SELECT story_id, description, created_at FROM stories;"
        rows = await self.conn.fetch(query)
        return [{'story_id': row['story_id'], 'description': row['description'], 'created_at': row['created_at']} for row in rows]
    
    # Создание вопроса
    async def create_question(self, worker_id: int, question: str):
        query = "INSERT INTO questions (worker_id, question, created_at) VALUES ($1, $2, $3) RETURNING question_id;"
        question_id = await self.conn.fetchval(query, worker_id, question, datetime.now())
        return question_id
    
    # Получение вопросов для модератора
    async def get_questions(self) -> List[Dict]:
        query = """
        SELECT q.question_id, q.question, q.created_at, u.username 
        FROM questions q
        LEFT JOIN users u ON q.worker_id = u.user_id
        ORDER BY q.created_at;
        """
        rows = await self.conn.fetch(query)
        return [{'question_id': row['question_id'], 'question': row['question'], 'created_at': row['created_at'], 'username': row['username']} for row in rows]
    
    # Ответ на вопрос
    async def answer_question(self, question_id: int, answer: str):
        query = "UPDATE questions SET answer = $2, answered_at = $3 WHERE question_id = $1;"
        await self.conn.execute(query, question_id, answer, datetime.now())
    
    # Получение ответов на вопросы для работника
    async def get_answers(self, worker_id: int) -> List[Dict]:
        query = """
        SELECT q.question, q.answer, q.answered_at
        FROM questions q
        WHERE q.worker_id = $1 AND q.answer IS NOT NULL
        ORDER BY q.answered_at;
        """
        rows = await self.conn.fetch(query, worker_id)
        return [{'question': row['question'], 'answer': row['answer'], 'answered_at': row['answered_at']} for row in rows]