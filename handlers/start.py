from aiogram import Router, types
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from middlewares.authentication import Authenticator

router = Router()

# Клавиатура для выбора роли
role_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Role 1"),
            KeyboardButton(text="Role 2"),
        ],
        [
            KeyboardButton(text="Role 3"),
            KeyboardButton(text="Role 4"),
        ],
    ],
    resize_keyboard=True
)

@router.message(Command("start"))
async def cmd_start(message: types.Message):
    print("Received /start command")  # Отладочная информация
    await message.answer("Привет! Добро пожаловать в нашего бота!", reply_markup=role_keyboard)

@router.message(lambda message: message.text in ["Role 1", "Role 2", "Role 3", "Role 4"])
async def choose_role(message: types.Message):
    authenticator = Authenticator()
    is_authenticated, response = authenticator.authenticate_user(message.from_user.username, message.text, message.text)
    if is_authenticated:
        await message.answer(response)
    else:
        await message.answer(response)