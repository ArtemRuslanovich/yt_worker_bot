import logging
from aiogram import Dispatcher, Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from database import SessionLocal, repository
from middlewares.authentication import Authenticator

router = Router()


class AuthStates(StatesGroup):
    waiting_for_role = State()
    waiting_for_username = State()
    waiting_for_password = State()


@router.message(Command(commands='start'))
async def cmd_start(message: types.Message, state: FSMContext):
    role_keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Admin")], [KeyboardButton(text="Manager")], [KeyboardButton(text="Worker")],
                  [KeyboardButton(text="Preview_maker")]],
        resize_keyboard=True,
    )
    await message.answer("Welcome to our bot! Choose your role:", reply_markup=role_keyboard)
    await state.set_state(AuthStates.waiting_for_role)


@router.message(AuthStates.waiting_for_role)
async def choose_role(message: types.Message, state: FSMContext):
    await state.update_data(chosen_role=message.text)
    await message.answer("Enter your username:")
    await state.set_state(AuthStates.waiting_for_username)


@router.message(AuthStates.waiting_for_username)
async def enter_username(message: types.Message, state: FSMContext):
    await state.update_data(username=message.text)
    await message.answer("Enter your password:")
    await state.set_state(AuthStates.waiting_for_password)


@router.message(AuthStates.waiting_for_password)
async def enter_password(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    username = user_data.get('username')
    password = message.text
    role = user_data.get('chosen_role')

    logging.info(f"Username: {username}, Role: {role}")  # Логирование для отладки

    with SessionLocal() as db_session:
        db_repository = repository.DatabaseRepository(db_session)
        authenticator = Authenticator(db_repository)
        authenticated, message_text = authenticator.authenticate_user(username, password, role)
        if authenticated:
            await message.answer(f"Authenticated as {role}.")
            await state.update_data(authenticated=True)  # Сохранение состояния аутентификации
        else:
            await message.answer("Authentication failed.")
            await state.update_data(authenticated=False)  # Сохранение состояния аутентификации

    await state.set_state(None)  # Завершение состояния


def register_handlers(dp: Dispatcher):
    dp.include_router(router)
