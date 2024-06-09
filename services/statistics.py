from database.repository import DatabaseRepository

class StatisticsService:
    def __init__(self, db_repository: DatabaseRepository):
        self.db_repository = db_repository

    def check_role(self, username, role):
        user = self.db_repository.get_user_by_username(username)
        if user:
            return user.role.name == role
        return False

    def get_worker_statistics(self, worker_id):
        tasks = self.db_repository.get_tasks_by_user_id(worker_id)
        on_time = 0
        missed = 0

        for task in tasks:
            if task.status == 'completed' and task.actual_completion_date <= task.deadline:
                on_time += 1
            elif task.status == 'completed' and task.actual_completion_date > task.deadline:
                missed += 1

        return {"on_time": on_time, "missed": missed}

    def get_preview_maker_statistics(self, preview_maker_id):
        previews = self.db_repository.get_previews_by_preview_maker_id(preview_maker_id)
        return len(previews)

    def get_channel_statistics(self, channel_id):
        videos = self.db_repository.get_videos_by_channel_id(channel_id)
        previews = self.db_repository.get_previews_by_channel_id(channel_id)
        return len(videos), len(previews)