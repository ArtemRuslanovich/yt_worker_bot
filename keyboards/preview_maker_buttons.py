from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

def preview_maker_main_keyboard():
    return InlineKeyboardMarkup(row_width=1).add(
        InlineKeyboardButton(text="Просмотр задач", callback_data="view_tasks")
    )

def task_selection_keyboard(tasks, add_back_button=False):
    markup = InlineKeyboardMarkup(row_width=1)
    for task in tasks:
        button = InlineKeyboardButton(text=task['title'], callback_data=f"select_task_{task['id']}")
        markup.add(button)
    if add_back_button:
        markup.add(InlineKeyboardButton(text="Назад", callback_data="go_back"))
    return markup

def task_action_keyboard(add_back_button=False):
    markup = InlineKeyboardMarkup(row_width=1).add(
        InlineKeyboardButton(text="Отправить на проверку", callback_data="send_review")
    )
    if add_back_button:
        markup.add(InlineKeyboardButton(text="Назад", callback_data="go_back"))
    return markup
