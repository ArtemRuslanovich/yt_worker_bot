import asyncio
import importlib
from aiogram import Bot, Dispatcher
from config import TOKEN
from services.reminders import RemindersService
from services.statistics import StatisticsService

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Register handlers
dp.include_router(StatisticsService.router)
dp.include_router(RemindersService.router)

for handler_module in ['handlers.manager', 'handlers.worker', 'handlers.preview_maker', 'handlers.admin']:
    dp.include_router(getattr(importlib.import_module(handler_module), 'router'))

# Start reminders service
async def start_reminders_service():
    await RemindersService.start()

async def on_startup(_):
    asyncio.create_task(start_reminders_service())

# Start bot
if __name__ == '__main__':
    updater = dp.start_polling(skip_updates=True, on_startup=on_startup)
