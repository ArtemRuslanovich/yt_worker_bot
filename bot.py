import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN, DATABASE_URL
from handlers.admin import register_handlers as register_admin_handlers
from handlers.manager import register_handlers as register_manager_handlers
from handlers.shooter import register_handlers as register_shooter_handlers
from handlers.preview_maker import register_handlers as register_preview_maker_handlers
from handlers.editor import register_handlers as register_editor_handlers
from handlers.moderator import register_handlers as register_moderator_handlers
from handlers.authentication import register_handlers as register_auth_handlers

from database.database import Database

async def on_startup(dp):
    print("Starting bot")
    # Инициализация соединения с базой данных (если требуется)
    dp['db'] = Database(dsn=DATABASE_URL)
    await dp['db'].connect()

async def on_shutdown(dp):
    print("Shutting down bot")
    # Закрытие соединения с базой данных
    await dp['db'].close()

def main():
    # Инициализация бота и диспетчера
    bot = Bot(token=BOT_TOKEN)
    storage = MemoryStorage()  # Вы можете использовать другой тип хранилища
    dp = Dispatcher(bot, storage=storage)

    
    # Регистрация обработчиков
    register_admin_handlers(dp)
    register_manager_handlers(dp)
    register_shooter_handlers(dp)
    register_preview_maker_handlers(dp)
    register_editor_handlers(dp)
    register_moderator_handlers(dp)
    register_auth_handlers(dp)
    
    # Запуск бота
    asyncio.run(dp.start_polling(bot, skip_updates=True, on_startup=on_startup))

if __name__ == "__main__":
    main()
