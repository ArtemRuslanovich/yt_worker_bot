from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

def manager_main_keyboard():
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("Создать задачу", callback_data='new_task'))
    keyboard.add(InlineKeyboardButton("Просмотреть задачи", callback_data='view_tasks'))
    keyboard.add(InlineKeyboardButton("Просмотреть сценарии", callback_data='view_stories'))
    return keyboard

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

def story_keyboard(stories):
    keyboard = InlineKeyboardMarkup()
    for story in stories:
        keyboard.add(InlineKeyboardButton(f"Сценарий от {story['created_at']}", callback_data=f"story_{story['story_id']}"))
    keyboard.add(InlineKeyboardButton("Назад", callback_data='manager_menu'))
    return keyboard