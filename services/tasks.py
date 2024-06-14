from database.models import Task
from database.repository import DatabaseRepository


class TasksService:
    def __init__(self, db_repository: DatabaseRepository):
        self.db_repository = db_repository

    def create_task(self, title, description, theme, worker_username, deadline, status, channel_id):
        task = Task(
            title=title,
            description=description,
            theme=theme,
            worker_username=worker_username,
            deadline=deadline,
            status=status,
            channel_id=channel_id
        )
        self.db_repository.session.add(task)
        self.db_repository.session.commit()
        return task
#
    def get_task_by_id(self, task_id):
        return self.db_repository.get_task_by_id(task_id)

    def update_task(self, task_id, status, actual_completion_date):
        return self.db_repository.update_task(task_id, status, actual_completion_date)

    def assign_task(self, task_id, worker_id):
        return self.db_repository.assign_task(task_id, worker_id)

    def get_tasks_by_worker_id(self, worker_id):
        return self.db_repository.get_tasks_by_worker_id(worker_id)

    def get_tasks_by_channel_id(self, channel_id):
        return self.db_repository.get_tasks_by_channel_id(channel_id)

    def get_overdue_tasks(self):
        return self.db_repository.get_overdue_tasks()
    
    def get_tasks_by_user_id(self, user_id):
        return self.db_repository.session.query(Task).filter_by(user_id=user_id).all()
    
    def get_tasks_by_status(self, status):
        return self.db_repository.session.query(Task).filter_by(status=status).all()