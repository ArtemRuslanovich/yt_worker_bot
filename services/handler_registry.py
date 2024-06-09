import logging
from aiogram import Dispatcher
from handlers import admin, manager, worker, preview_maker, moderator  # Убедитесь, что импортирован модуль модератора

def register_role_handlers(role: str, dp: Dispatcher):
    role_handlers = {
        "Admin": admin.register_handlers,
        "Manager": manager.register_handlers,
        "Worker": worker.register_handlers,
        "Preview_maker": preview_maker.register_handlers,
        "Moderator": moderator.register_handlers  # Добавление обработчика для модератора
    }

    handler_function = role_handlers.get(role)
    if handler_function:
        handler_function(dp)
    else:
        logging.error(f"No handlers found for role: {role}")
        raise ValueError(f"No handlers found for role: {role}")