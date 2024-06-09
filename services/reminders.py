import asyncio
from aiogram import Bot, Router
from database.repository import DatabaseRepository
from datetime import timedelta
from database import SessionLocal

db_session = SessionLocal()

# Define the router outside the class
router = Router()

class RemindersService:
    def __init__(self, bot: Bot):
        self.bot = bot
        self.repository = DatabaseRepository(db_session)

    async def send_reminders(self):
        overdue_tasks = self.repository.get_overdue_tasks()

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