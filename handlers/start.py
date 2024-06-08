from aiogram import Router, types, Dispatcher, Bot
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from middlewares.authentication import Authenticator
from database import SessionLocal, repository
from services import handler_registry as registry


router = Router()

# Клавиатура для выбора роли
role_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Admin"), KeyboardButton(text="Manager")],
        [KeyboardButton(text="Worker"), KeyboardButton(text="Preview_maker")],
    ],
    resize_keyboard=True,
)

class AuthStates(StatesGroup):
    waiting_for_role = State()
    waiting_for_username = State()
    waiting_for_password = State()

@router.message(Command(commands='start'))
async def cmd_start(message: types.Message, state: FSMContext):
    print("Received /start command")  # Отладочная информация
    await message.answer("Привет! Добро пожаловать в нашего бота!", reply_markup=role_keyboard)
    await state.set_state(AuthStates.waiting_for_role)

@router.message(AuthStates.waiting_for_role, lambda message: message.text in ["Admin", "Manager", "Worker", "Preview_maker"])
async def choose_role(message: types.Message, state: FSMContext):
    print(f"Role chosen: {message.text}")  # Отладочная информация
    await state.update_data(chosen_role=message.text)
    await message.answer("Введите ваш логин:")
    await state.set_state(AuthStates.waiting_for_username)

@router.message(AuthStates.waiting_for_username)
async def enter_username(message: types.Message, state: FSMContext):
    await state.update_data(username=message.text)
    await message.answer("Введите ваш пароль:")
    await state.set_state(AuthStates.waiting_for_password)

@router.message(AuthStates.waiting_for_password)
async def enter_password(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    username = user_data['username']
    password = message.text
    role = user_data['chosen_role']

    # Создаем экземпляр сессии и репозитория базы данных
    db_session = SessionLocal()
    db_repository = repository.DatabaseRepository(db_session)

    # Создаем экземпляр Authenticator
    authenticator = Authenticator(db_repository)

    # Проверяем авторизацию пользователя
    authenticated, message_text = authenticator.authenticate_user(username, password, role)

    if authenticated:
        await message.answer(f"Вы выбрали роль: {role}. {message_text}")
        # Предоставляем доступ к функционалу роли
        registry.register_role_handlers(role)
    else:
        await message.answer(message_text)

    await state.clear()