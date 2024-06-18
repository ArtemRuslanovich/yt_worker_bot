from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

def channel_keyboard(channels):
    markup = InlineKeyboardMarkup(row_width=1)
    for channel in channels:
        button = InlineKeyboardButton(text=channel['name'], callback_data=f"channel_{channel['id']}")
        markup.add(button)
    return markup

def task_keyboard(tasks):
    markup = InlineKeyboardMarkup(row_width=1)
    for task in tasks:
        button = InlineKeyboardButton(text=task['title'], callback_data=f"task_{task['id']}")
        markup.add(button)
    return markup

def task_approval_keyboard():
    return InlineKeyboardMarkup().add(
        InlineKeyboardButton(text="Одобрить", callback_data="approve"),
        InlineKeyboardButton(text="На доработку", callback_data="revise")
    )