from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

def channel_list_keyboard(channels):
    markup = InlineKeyboardMarkup(row_width=1)
    for channel in channels:
        button = InlineKeyboardButton(text=channel['name'], callback_data=f"manage_channel_{channel['id']}")
        markup.add(button)
    return markup

def worker_list_keyboard(workers):
    markup = InlineKeyboardMarkup(row_width=1)
    for worker in workers:
        button = InlineKeyboardButton(text=worker['username'], callback_data=f"manage_worker_{worker['user_id']}")
        markup.add(button)
    return markup

def statistics_keyboard():
    return InlineKeyboardMarkup().add(
        InlineKeyboardButton(text="Статистика по каналам", callback_data="stats_channels"),
        InlineKeyboardButton(text="Статистика по работникам", callback_data="stats_workers")
    )