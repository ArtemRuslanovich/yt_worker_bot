from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

def moderator_main_keyboard():
    return InlineKeyboardMarkup(row_width=1).add(
        InlineKeyboardButton(text="Создать сюжет", callback_data="create_story"),
        InlineKeyboardButton(text="Просмотр задач", callback_data="view_tasks"),
        InlineKeyboardButton("Добавить доход за месяц", callback_data='add_monthly_income')
    )

def task_list_keyboard(tasks, add_back_button=False):
    markup = InlineKeyboardMarkup(row_width=1)
    for task in tasks:
        button = InlineKeyboardButton(text=task['title'], callback_data=f"review_task_{task['id']}")
        markup.add(button)
    if add_back_button:
        markup.add(InlineKeyboardButton(text="Назад", callback_data="go_back"))
    return markup

def task_review_keyboard(add_back_button=False):
    markup = InlineKeyboardMarkup(row_width=1).add(
        InlineKeyboardButton(text="Одобрить", callback_data="approve_task"),
        InlineKeyboardButton(text="На доработку", callback_data="revise_task")
    )
    if add_back_button:
        markup.add(InlineKeyboardButton(text="Назад", callback_data="go_back"))
    return markup
