from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

def manager_main_keyboard():
    return InlineKeyboardMarkup(row_width=1).add(
        InlineKeyboardButton(text="Создать задачу", callback_data="new_task"),
        InlineKeyboardButton(text="Просмотр задач", callback_data="view_tasks")
    )

def channel_keyboard(channels, add_back_button=False):
    markup = InlineKeyboardMarkup(row_width=1)
    for channel in channels:
        button = InlineKeyboardButton(text=channel['name'], callback_data=f"channel_{channel['channel_id']}")
        markup.add(button)
    if add_back_button:
        markup.add(InlineKeyboardButton(text="Назад", callback_data="go_back"))
    return markup

def worker_keyboard(workers, add_back_button=False):
    markup = InlineKeyboardMarkup(row_width=1)
    for worker in workers:
        button = InlineKeyboardButton(text=worker['username'], callback_data=f"worker_{worker['user_id']}")
        markup.add(button)
    if add_back_button:
        markup.add(InlineKeyboardButton(text="Назад", callback_data="go_back"))
    return markup

def task_keyboard(tasks, add_back_button=False):
    markup = InlineKeyboardMarkup(row_width=1)
    for task in tasks:
        button = InlineKeyboardButton(text=task['title'], callback_data=f"task_{task['id']}")
        markup.add(button)
    if add_back_button:
        markup.add(InlineKeyboardButton(text="Назад", callback_data="go_back"))
    return markup

def task_approval_keyboard(add_back_button=False):
    markup = InlineKeyboardMarkup(row_width=1).add(
        InlineKeyboardButton(text="Одобрить", callback_data="approve"),
        InlineKeyboardButton(text="Отправить на доработку", callback_data="revise")
    )
    if add_back_button:
        markup.add(InlineKeyboardButton(text="Назад", callback_data="go_back"))
    return markup
