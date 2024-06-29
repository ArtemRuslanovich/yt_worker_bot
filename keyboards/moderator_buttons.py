from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

def moderator_main_keyboard():
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("Просмотреть каналы", callback_data="view_channels"))
    keyboard.add(InlineKeyboardButton("Просмотреть работников", callback_data="view_workers"))
    keyboard.add(InlineKeyboardButton("Создать сценарий", callback_data="create_story"))
    keyboard.add(InlineKeyboardButton("Вопросы", callback_data="view_questions"))
    keyboard.add(InlineKeyboardButton("Отправить файл", callback_data="send_file"))
    keyboard.add(InlineKeyboardButton("Просмотреть задачи", callback_data="view_tasks"))
    return keyboard

def channel_list_keyboard(channels, add_back_button=False):
    keyboard = InlineKeyboardMarkup()
    for channel in channels:
        keyboard.add(InlineKeyboardButton(channel['name'], callback_data=f"channel_{channel['channel_id']}"))
    if add_back_button:
        keyboard.add(InlineKeyboardButton("Назад", callback_data="moderator_menu"))
    return keyboard

def worker_list_keyboard(workers, add_back_button=False):
    keyboard = InlineKeyboardMarkup()
    for worker in workers:
        keyboard.add(InlineKeyboardButton(worker['username'], callback_data=f"manage_worker_{worker['user_id']}"))
    if add_back_button:
        keyboard.add(InlineKeyboardButton("Назад", callback_data="moderator_menu"))
    return keyboard

def worker_info_keyboard(add_back_button=False):
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("Добавить затраты", callback_data="add_worker_expense"))
    keyboard.add(InlineKeyboardButton("Добавить ошибку", callback_data="add_worker_error"))
    if add_back_button:
        keyboard.add(InlineKeyboardButton("Назад", callback_data="view_workers"))
    return keyboard

def task_keyboard(tasks):
    keyboard = InlineKeyboardMarkup()
    for task in tasks:
        keyboard.add(InlineKeyboardButton(task['title'], callback_data=f"task_{task['id']}"))
    keyboard.add(InlineKeyboardButton("Назад", callback_data="moderator_menu"))
    return keyboard

def question_keyboard(questions):
    keyboard = InlineKeyboardMarkup()
    for question in questions:
        keyboard.add(InlineKeyboardButton(question['question'], callback_data=f"question_{question['id']}"))
    keyboard.add(InlineKeyboardButton("Назад", callback_data="moderator_menu"))
    return keyboard

def task_approval_keyboard(add_back_button=False):
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("Одобрить", callback_data="approve"))
    keyboard.add(InlineKeyboardButton("Отправить на доработку", callback_data="revise"))
    if add_back_button:
        keyboard.add(InlineKeyboardButton("Назад", callback_data="view_tasks"))
    return keyboard
