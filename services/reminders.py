import asyncio
from aiogram import Bot, Router, F
from aiogram.types import Message
from database import repository
from datetime import timedelta

# Define the router outside the class
router = Router()

class RemindersService:
    def __init__(self, bot: Bot):
        self.bot = bot

    async def send_reminders(self):
        # Get all tasks that are due today or overdue
        overdue_tasks = repository.get_overdue_tasks()

        for task in overdue_tasks:
            user = task.user
            if user.role.name == 'Worker':
                # Send a reminder to the worker
                await self.bot.send_message(
                    user.username,
                    f'Напоминание: Задание "{task.title}" не выполнено. Нужно сделать как можно скорее.'
                )

    async def schedule_reminders(self):
        while True:
            await self.send_reminders()
            await asyncio.sleep(timedelta(hours=1).total_seconds())

    @staticmethod
    async def start(bot: Bot):
        service = RemindersService(bot)
        await service.schedule_reminders()

# Export the router to be included in the main bot script
RemindersService.router = router