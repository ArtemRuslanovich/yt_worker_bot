from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

def main_admin_keyboard():
    return InlineKeyboardMarkup(row_width=1).add(
        InlineKeyboardButton(text="Создать канал", callback_data="create_channel"),
        InlineKeyboardButton(text="Просмотр каналов", callback_data="view_channels"),
        InlineKeyboardButton(text="Просмотр работников", callback_data="view_workers"),
        InlineKeyboardButton("Добавить доход за месяц", callback_data='add_monthly_income'),
        InlineKeyboardButton(text="Статистика", callback_data="view_statistics")
    )

def channel_list_keyboard(channels, add_back_button=False):
    markup = InlineKeyboardMarkup(row_width=1)
    for channel in channels:
        button = InlineKeyboardButton(text=channel['name'], callback_data=f"manage_channel_{channel['id']}")
        markup.add(button)
    if add_back_button:
        markup.add(InlineKeyboardButton(text="Назад", callback_data="go_back"))
    return markup

def worker_list_keyboard(workers, add_back_button=False):
    markup = InlineKeyboardMarkup(row_width=1)
    for worker in workers:
        button = InlineKeyboardButton(text=worker['username'], callback_data=f"manage_worker_{worker['user_id']}")
        markup.add(button)
    if add_back_button:
        markup.add(InlineKeyboardButton(text="Назад", callback_data="go_back"))
    return markup

def statistics_keyboard(add_back_button=False):
    markup = InlineKeyboardMarkup(row_width=1).add(
        InlineKeyboardButton(text="Статистика по каналам", callback_data="stats_channels"),
        InlineKeyboardButton(text="Статистика по работникам", callback_data="stats_workers")
    )
    if add_back_button:
        markup.add(InlineKeyboardButton(text="Назад", callback_data="go_back"))
    return markup

def channel_keyboard(channels, add_back_button=False):
    markup = InlineKeyboardMarkup(row_width=1)
    for channel in channels:
        button = InlineKeyboardButton(text=channel['name'], callback_data=f"select_channel_income_{channel['id']}")
        markup.add(button)
    if add_back_button:
        markup.add(InlineKeyboardButton(text="Назад", callback_data="go_back"))
    return markup