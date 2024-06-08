from aiogram import Router, F
from aiogram.types import Message
from database import repository

# Define the router outside the class
router = Router()

class StatisticsService:
    def __init__(self, db_repository):
        self.db_repository = db_repository

    @staticmethod
    @router.message(F.text == '/stats')
    async def stats_handler(message: Message):
        user_id = message.from_user.id
        if message.chat.type == 'private':
            # Get worker statistics
            on_time, missed = StatisticsService.get_worker_statistics(user_id)
            await message.answer(f"On time: {on_time}\nMissed: {missed}")
        else:
            # Get channel statistics
            videos, previews = StatisticsService.get_channel_statistics(message.chat.id)
            await message.answer(f"Videos: {videos}\nPreviews: {previews}")

    def get_worker_statistics(self, worker_id):
        tasks = self.db_repository.get_tasks_by_worker_id(worker_id)
        on_time = 0
        missed = 0

        for task in tasks:
            if task.status == 'completed' and task.actual_completion_date <= task.deadline:
                on_time += 1
            elif task.status == 'completed' and task.actual_completion_date > task.deadline:
                missed += 1

        return on_time, missed

    def get_preview_maker_statistics(self, preview_maker_id):
        previews = self.db_repository.get_previews_by_preview_maker_id(preview_maker_id)
        return len(previews)

    def get_channel_statistics(self, channel_id):
        videos = self.db_repository.get_videos_by_channel_id(channel_id)
        previews = self.db_repository.get_previews_by_channel_id(channel_id)
        return len(videos), len(previews)
    
    def check_role(self, user_id, role):
        # Get user's role from the database
        user_role = self.db_repository.get_user_role(user_id)
        return user_role == role

# Export the router to be included in the main bot script
StatisticsService.router = router
