from aiogram import Dispatcher
from handlers import admin, manager, worker, preview_maker

def register_role_handlers(dp: Dispatcher, role: str):
    if role == "Admin":
        admin.register_handlers(dp)
    elif role == "Manager":
        manager.register_handlers(dp)
    elif role == "Worker":
        worker.register_handlers(dp)
    elif role == "Preview_maker":
        preview_maker.register_handlers(dp)