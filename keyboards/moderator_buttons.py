from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

def task_list_keyboard(tasks):
    markup = InlineKeyboardMarkup(row_width=1)
    for task in tasks:
        button = InlineKeyboardButton(text=task['title'], callback_data=f"review_task_{task['id']}")
        markup.add(button)
    return markup

def task_review_keyboard():
    return InlineKeyboardMarkup().add(
        InlineKeyboardButton(text="Одобрить", callback_data="approve_task"),
        InlineKeyboardButton(text="На доработку", callback_data="revise_task")
    )