from aiogram import Dispatcher, types
from aiogram.fsm.context import FSMContext
from services.auth_service import authenticate
from states.auth_states import AuthStates

async def cmd_start(message: types.Message):
    reply_markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    reply_markup.add("Admin", "Manager", "Moderator", "Shooter", "Editor", "Preview Maker")
    await message.answer("Welcome to our bot! Choose your role:", reply_markup=reply_markup)
    await AuthStates.waiting_for_role.set()

async def role_chosen(message: types.Message, state: FSMContext):
    role = message.text.lower()
    await state.update_data(chosen_role=role)
    await message.answer("Enter your username:", reply_markup=types.ReplyKeyboardRemove())
    await AuthStates.waiting_for_username.set()

async def username_entered(message: types.Message, state: FSMContext):
    await state.update_data(username=message.text)
    await message.answer("Enter your password:")
    await AuthStates.waiting_for_password.set()

async def password_entered(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    username = user_data['username']
    password = message.text
    role = user_data['chosen_role']

    # Исправленный вызов асинхронной функции authenticate
    if await authenticate(username, password, role):
        await message.answer(f"Authenticated as {role}.")
        await state.update_data(authenticated=True)
        await state.set_state(getattr(AuthStates, role))  # Переход в состояние роли
    else:
        await message.answer("Authentication failed. Try again.")
        await state.finish()

def register_handlers(dp: Dispatcher):
    dp.register_message_handler(cmd_start, commands="start", state="*")
    dp.register_message_handler(role_chosen, state=AuthStates.waiting_for_role)
    dp.register_message_handler(username_entered, state=AuthStates.waiting_for_username)
    dp.register_message_handler(password_entered, state=AuthStates.waiting_for_password)
