from aiogram import Router, types, Dispatcher
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from middlewares.authentication import Authenticator

router = Router()

# Клавиатура для выбора роли
role_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Admin"), KeyboardButton(text="Manager")],
        [KeyboardButton(text="Worker"), KeyboardButton(text="Preview_maker")],
    ],
    resize_keyboard=True,
)

@router.message(Command(commands='start'))
async def cmd_start(message: types.Message, dp: Dispatcher):
    print("Received /start command")  # Отладочная информация
    await message.answer("Привет! Добро пожаловать в нашего бота!", reply_markup=role_keyboard)

@router.message(lambda message: message.text in ["Admin", "Manager", "Worker", "Preview_maker"])
async def choose_role(message: types.Message, dp: Dispatcher):
    print(f"Role chosen: {message.text}")  # Отладочная информация
    username = message.from_user.username  # Получаем имя пользователя
    role = message.text  # Получаем выбранную роль

    # Создаем экземпляр Authenticator
    authenticator = Authenticator()

    # Проверяем авторизацию пользователя
    authenticated, message_text = authenticator.authenticate_user(username, None, role)

    if authenticated:
        await message.answer(f"Вы выбрали роль: {message.text}. {message_text}")
        # Предоставляем доступ к функционалу роли
        register_role_handlers(dp, role)
    else:
        await message.answer(message_text)