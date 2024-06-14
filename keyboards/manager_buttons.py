from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_manager_buttons():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Создать задачу", callback_data="create_task")],
        [InlineKeyboardButton(text="Просмотреть задачи", callback_data="view_task")],
        [InlineKeyboardButton(text="Изменить статус задачи", callback_data="check_task")],
        [InlineKeyboardButton(text="Установить зарплату", callback_data="set_salary")]
    ])