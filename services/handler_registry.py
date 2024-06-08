from aiogram import Dispatcher
from handlers import admin, manager, worker, preview_maker
from aiogram.fsm.context import FSMContext


def register_role_handlers(role: str):
    if role == "Admin":
        admin.register_handlers(Dispatcher)
    elif role == "Manager":
        manager.register_handlers(Dispatcher)
    elif role == "Worker":
        worker.register_handlers(Dispatcher)
    elif role == "Preview_maker":
        preview_maker.register_handlers(Dispatcher)