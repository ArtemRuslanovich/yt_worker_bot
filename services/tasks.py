from database.repository import DatabaseRepository


class TasksService:
    def __init__(self, db_repository: DatabaseRepository):
        self.db_repository = db_repository

    def create_task(self, user_id, title, description, deadline, status, channel_id):
        return self.db_repository.create_task(user_id, title, description, deadline, status, channel_id)

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