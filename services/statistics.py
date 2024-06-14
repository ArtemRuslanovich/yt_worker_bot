from database.repository import DatabaseRepository


class StatisticsService:
    def __init__(self, db_repository: DatabaseRepository):
        self.db_repository = db_repository

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
#
    def get_channel_statistics(self, channel_id):
        videos = self.db_repository.get_videos_by_channel_id(channel_id)
        previews = self.db_repository.get_previews_by_channel_id(channel_id)
        return len(videos), len(previews)

    def get_all_channels_statistics(self):
        channels = self.db_repository.get_all_channels()
        total_expenses = 0
        total_payments = 0
        total_videos = 0
        total_previews = 0

        for channel in channels:
            total_expenses += self.db_repository.get_total_expenses_for_channel(channel.id)
            total_payments += self.db_repository.get_total_payments_for_channel(channel.id)
            total_videos += len(self.db_repository.get_videos_by_channel_id(channel.id))
            total_previews += len(self.db_repository.get_previews_by_channel_id(channel.id))

        return {
            "total_channels": len(channels),
            "total_expenses": total_expenses,
            "total_payments": total_payments,
            "total_videos": total_videos,
            "total_previews": total_previews
        }

    def get_statistics(self):
        statistics = {
            'channels': [],
            'workers': []
        }

        channels = self.db_repository.get_all_channels()
        for channel in channels:
            channel_stats = {
                'name': channel.name,
                'expenses': sum(expense.amount for expense in channel.expenses),
                'salaries': sum(worker.salary for worker in channel.workers)
            }
            statistics['channels'].append(channel_stats)

        workers = self.db_repository.get_all_users_by_role('Worker')
        for worker in workers:
            worker_stats = {
                'username': worker.username,
                'expenses': sum(expense.amount for expense in worker.expenses),
                'salary': worker.salary
            }
            statistics['workers'].append(worker_stats)

        return statistics
