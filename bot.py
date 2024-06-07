import asyncio
import importlib
from aiogram import Bot, Dispatcher
from config import TOKEN
from services.reminders import RemindersService
from services.statistics import StatisticsService
from database import SessionLocal

db_session = SessionLocal()
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Register handlers
dp.include_router(StatisticsService.router)
dp.include_router(RemindersService.router)

for handler_module in ['handlers.manager', 'handlers.worker', 'handlers.preview_maker', 'handlers.admin']:
    dp.include_router(getattr(importlib.import_module(handler_module), 'router'))

# Start reminders service
async def start_reminders_service():
    service = RemindersService(bot, db_session)
    await service.schedule_reminders()

async def on_startup(_):
    await start_reminders_service()

# Start bot
if __name__ == '__main__':
    asyncio.run(on_startup(None))  # Запустить on_startup как асинхронную функцию
    dp.start_polling(skip_updates=True)
