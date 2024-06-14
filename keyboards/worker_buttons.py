from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_worker_buttons():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Принять задачу", callback_data="accept_task")],
        [InlineKeyboardButton(text="Сдать задачу", callback_data="submit_task")],
        [InlineKeyboardButton(text="Просмотреть задачи", callback_data="view_tasks")]
    ])