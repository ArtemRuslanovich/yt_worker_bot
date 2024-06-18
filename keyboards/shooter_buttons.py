from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

def task_selection_keyboard(tasks):
    markup = InlineKeyboardMarkup(row_width=1)
    for task in tasks:
        button = InlineKeyboardButton(text=task['title'], callback_data=f"select_task_{task['id']}")
        markup.add(button)
    return markup

def task_action_keyboard():
    return InlineKeyboardMarkup().add(
        InlineKeyboardButton(text="Отправить на проверку", callback_data="send_review")
    )