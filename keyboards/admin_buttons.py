from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_admin_buttons():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Просмотреть статистику", callback_data="view_statistics")],
        [InlineKeyboardButton(text="Создать канал", callback_data="create_channel")],
        [InlineKeyboardButton(text="Просмотреть каналы", callback_data="view_channels")]
    ])