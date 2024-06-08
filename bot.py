import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand
from config import TOKEN
from database import SessionLocal
from handlers.start import router as start_router
from handlers.admin import router as admin_router
from handlers.manager import router as manager_router
from handlers.worker import router as worker_router
from handlers.preview_maker import router as preview_maker_router

bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot=bot, storage=storage)

def register_all_handlers():
    dp.include_router(start_router)
    dp.include_router(admin_router)
    dp.include_router(manager_router)
    dp.include_router(worker_router)
    dp.include_router(preview_maker_router)
    # Если есть дополнительные роутеры, добавьте их сюда

async def on_startup():
    await bot.set_my_commands([
        BotCommand(command="/start", description="Start the bot"),
        BotCommand(command="/create_channel", description="Create a channel"),
        BotCommand(command="/log_payment", description="Log a payment"),
        # Добавьте описание других команд, если они у вас есть
    ])
    print("Бот запущен и готов к работе!")

if __name__ == "__main__":
    register_all_handlers()
    asyncio.run(dp.start_polling(bot, skip_updates=True, on_startup=on_startup))