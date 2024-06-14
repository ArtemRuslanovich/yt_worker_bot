from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

def get_moderator_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=2)
    buttons = [
        InlineKeyboardButton(text="Отправить сообщение", callback_data="send_message"),
        InlineKeyboardButton(text="Лог расходов", callback_data="log_expense"),
        InlineKeyboardButton(text="Установить зп", callback_data="set_salary")
    ]
    keyboard.add(*buttons)
    return keyboard