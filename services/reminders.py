import asyncio
from aiogram import types, Bot
from database import repository
from datetime import datetime, timedelta

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
                    f'Reminder: Your task "{task.title}" is overdue. Please submit it as soon as possible.'
                )

    async def schedule_reminders(self):
        while True:
            await self.send_reminders()
            await asyncio.sleep(timedelta(hours=1).total_seconds())