from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_preview_maker_buttons():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Принять задачу", callback_data="pm_accept_task")],
        [InlineKeyboardButton(text="Сдать задачу", callback_data="pm_submit_task")],
        [InlineKeyboardButton(text="Просмотреть задачи", callback_data="pm_view_tasks")]
    ])