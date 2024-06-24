from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from keyboards.moderator_buttons import moderator_main_keyboard, task_list_keyboard, task_review_keyboard
from states.auth_states import AuthStates
from database.database import Database
from datetime import datetime

class AuthStates(StatesGroup):
    moderator = State()
    creating_story = State()
    reviewing_task = State()
    adding_monthly_income = State()

async def moderator_menu(message: types.Message, state: FSMContext):
    await message.answer("Меню модератора:", reply_markup=moderator_main_keyboard())
    await AuthStates.moderator.set()

async def create_story(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.message.answer("Введите сюжет для новой задачи:")
    await AuthStates.creating_story.set()

async def handle_new_story(message: types.Message, state: FSMContext):
    db: Database = message.bot['db']
    await db.create_story(message.text)
    await message.answer("Сюжет создан.")
    await moderator_menu(message, state)

async def view_tasks(callback_query: types.CallbackQuery, state: FSMContext):
    db: Database = callback_query.message.bot['db']
    tasks = await db.get_tasks_for_review()
    await callback_query.message.answer("Список задач для проверки:", reply_markup=task_list_keyboard(tasks, add_back_button=True))

async def review_task(callback_query: types.CallbackQuery, state: FSMContext):
    task_id = callback_query.data.split("_")[2]
    db: Database = callback_query.message.bot['db']
    task = await db.get_task_details(task_id)
    await callback_query.message.answer(f"Детали задачи: {task['details']}", reply_markup=task_review_keyboard(add_back_button=True))

async def approve_task(callback_query: types.CallbackQuery, state: FSMContext):
    task_id = callback_query.data.split("_")[2]
    db: Database = callback_query.message.bot['db']
    await db.update_task_status(task_id, 'approved')
    await callback_query.message.answer("Задача одобрена.")
    await moderator_menu(callback_query.message)

async def revise_task(callback_query: types.CallbackQuery, state: FSMContext):
    task_id = callback_query.data.split("_")[2]
    db: Database = callback_query.message.bot['db']
    await db.update_task_status(task_id, 'needs_revision')
    await callback_query.message.answer("Задача отправлена на доработку.")
    await moderator_menu(callback_query.message)

async def add_monthly_income(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.message.answer("Введите ID канала и сумму дохода за текущий месяц (разделены пробелом):")
    await AuthStates.adding_monthly_income.set()

async def handle_monthly_income(message: types.Message, state: FSMContext):
    try:
        channel_id, amount = message.text.split()
        channel_id = int(channel_id)
        amount = float(amount)
        db: Database = message.bot['db']
        await db.add_monthly_income_to_channel(channel_id, amount, "Доход за текущий месяц")
        await message.answer(f"Доход в размере {amount} успешно добавлен для канала с ID {channel_id}.")
    except ValueError:
        await message.answer("Некорректный формат ввода. Введите ID канала и сумму дохода (разделены пробелом).")
    except Exception as e:
        await message.answer(f"Произошла ошибка при добавлении дохода: {e}")

    await moderator_menu(message, state)

def register_handlers(dp: Dispatcher):
    dp.register_callback_query_handler(moderator_menu, lambda c: c.data == 'moderator', state='*')
    dp.register_callback_query_handler(create_story, lambda c: c.data == 'create_story', state=AuthStates.moderator)
    dp.register_message_handler(handle_new_story, content_types=types.ContentTypes.TEXT, state=AuthStates.creating_story)
    dp.register_callback_query_handler(view_tasks, lambda c: c.data == 'view_tasks', state=AuthStates.moderator)
    dp.register_callback_query_handler(review_task, lambda c: c.data.startswith('review_task_'), state=AuthStates.moderator)
    dp.register_callback_query_handler(approve_task, lambda c: c.data.startswith('approve_task_'), state=AuthStates.moderator)
    dp.register_callback_query_handler(revise_task, lambda c: c.data.startswith('revise_task_'), state=AuthStates.moderator)
    dp.register_callback_query_handler(add_monthly_income, lambda c: c.data == 'add_monthly_income', state='*')
    dp.register_message_handler(handle_monthly_income, content_types=types.ContentTypes.TEXT, state=AuthStates.adding_monthly_income)