import asyncio
import importlib
from aiogram import Bot, Dispatcher
from config import TOKEN
from services.reminders import RemindersService
from services.statistics import StatisticsService
from database import SessionLocal
from aiogram import Router

db_session = SessionLocal()
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Register routers
routers = ['handlers.manager', 'handlers.worker', 'handlers.preview_maker', 'handlers.admin', 'handlers.start']

for router_module in routers:
    module = importlib.import_module(router_module)
    dp.include_router(module.router)

# Start reminders service
async def start_reminders_service():
    service = RemindersService(bot, db_session)
    await service.schedule_reminders()

async def on_startup():
    await start_reminders_service()

# Start bot
if __name__ == '__main__':
    asyncio.run(on_startup())
    dp.start_polling(bot, skip_updates=True)