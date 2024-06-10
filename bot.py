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

async def on_startup():
    await bot.set_my_commands([
        BotCommand(command="/start", description="Start the bot"),
        BotCommand(command="/create_channel", description="Create a channel"),
        BotCommand(command="/send_message", description="Send a message to a channel"),
        BotCommand(command="/set_bonus_percentage", description="Set bonus percentage"),
        BotCommand(command="/calculate_total_payouts", description="Calculate total payouts"),
        BotCommand(command="/log_expense", description="Log an expense"),
        BotCommand(command="/statistics", description="Show statistics"),
        BotCommand(command="/create_task", description="Create a task"),
        BotCommand(command="/submit_task", description="Submit a task"),
        BotCommand(command="/view_tasks", description="View tasks"),
        BotCommand(command="/submit_preview", description="Submit a preview"),
        BotCommand(command="/view_previews", description="View previews"),
        BotCommand(command="/set_salary", description="Set salary"),
    ])
    print("Бот запущен и готов к работе!")

if __name__ == "__main__":
    register_all_handlers()
    asyncio.run(dp.start_polling(bot, skip_updates=True, on_startup=on_startup))