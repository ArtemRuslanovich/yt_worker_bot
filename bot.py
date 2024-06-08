import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand
from config import TOKEN
from handlers import start, manager, worker, preview_maker, admin
from services.reminders import RemindersService
from database import SessionLocal

bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)
db_session = SessionLocal()  # Инициализация базы данных

# Register handlers
dp.include_router(start.router)
print("Start router included")  # Отладочная информация

dp.include_router(manager.router)
print("Manager router included")  # Отладочная информация

dp.include_router(worker.router)
print("Worker router included")  # Отладочная информация

dp.include_router(preview_maker.router)
print("Preview maker router included")  # Отладочная информация

dp.include_router(admin.router)
print("Admin router included")  # Отладочная информация

async def on_startup():
    print("on_startup is running")  # Отладочная информация
    await bot.set_my_commands([BotCommand(command="/start", description="Start the bot")])
    print("Commands have been set")  # Отладочная информация

    print("Initializing RemindersService...")  # Отладочная информация
    service = RemindersService(bot, db_session)
    print("RemindersService initialized")  # Отладочная информация
    # Не вызываем методы внутри RemindersService для проверки инициализации

dp.startup.register(on_startup)

print("Bot is starting...")  # Отладочная информация
try:
    asyncio.run(dp.start_polling(bot, skip_updates=True))
except Exception as e:
    print(f"Error: {e}")  # Отладочная информация