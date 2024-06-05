from database import repository

class StatisticsService:
    def __init__(self):
        pass

    def get_worker_statistics(self, worker_id):
        tasks = repository.get_tasks_by_worker_id(worker_id)
        on_time = 0
        missed = 0

        for task in tasks:
            if task.status == 'completed' and task.actual_completion_date <= task.deadline:
                on_time += 1
            elif task.status == 'completed' and task.actual_completion_date > task.deadline:
                missed += 1

        return on_time, missed

    def get_preview_maker_statistics(self, preview_maker_id):
        previews = repository.get_previews_by_preview_maker_id(preview_maker_id)
        return len(previews)

    def get_channel_statistics(self, channel_id):
        videos = repository.get_videos_by_channel_id(channel_id)
        previews = repository.get_previews_by_channel_id(channel_id)
        return len(videos), len(previews)