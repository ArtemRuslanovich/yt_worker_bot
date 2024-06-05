from database import repository

class TasksService:
    def __init__(self):
        pass

    def create_task(self, title, description, thumbnail_draft, worker_id, deadline, channel_id):
        task = repository.create_task(title, description, thumbnail_draft, worker_id, deadline, channel_id)
        return task

    def get_task_by_id(self, task_id):
        task = repository.get_task_by_id(task_id)
        return task

    def update_task(self, task_id, status, actual_completion_date):
        task = repository.update_task(task_id, status, actual_completion_date)
        return task

    def assign_task(self, task_id, worker_id):
        task = repository.assign_task(task_id, worker_id)
        return task

    def get_tasks_by_worker_id(self, worker_id):
        tasks = repository.get_tasks_by_worker_id(worker_id)
        return tasks

    def get_tasks_by_channel_id(self, channel_id):
        tasks = repository.get_tasks_by_channel_id(channel_id)
        return tasks

    def get_overdue_tasks(self):
        tasks = repository.get_overdue_tasks()
        return tasks