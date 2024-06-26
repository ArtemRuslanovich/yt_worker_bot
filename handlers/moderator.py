from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from keyboards.moderator_buttons import channel_keyboard, moderator_main_keyboard, task_list_keyboard, task_review_keyboard
from states.auth_states import AuthStates
from database.database import Database
from datetime import datetime

class AuthStates(StatesGroup):
    moderator = State()
    creating_story = State()
    reviewing_task = State()
    choosing_task_channel = State()  # Новое состояние для выбора канала при создании задачи
    entering_task_details = State()  # Новое состояние для ввода деталей задачи

async def moderator_menu(message: types.Message, state: FSMContext):
    await message.answer("Меню модератора:", reply_markup=moderator_main_keyboard())
    await AuthStates.moderator.set()

async def go_back(callback_query: types.CallbackQuery, state: FSMContext):
    await moderator_menu(callback_query.message, state)

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

async def start_task_creation(callback_query: types.CallbackQuery, state: FSMContext):
    db: Database = callback_query.message.bot['db']
    channels = await db.get_channels()  # Получение списка каналов из БД
    await AuthStates.choosing_task_channel.set()
    await callback_query.message.answer("Выберите канал:", reply_markup=channel_keyboard(channels, add_back_button=True))

async def choose_task_channel(callback_query: types.CallbackQuery, state: FSMContext):
    await state.update_data(channel_id=int(callback_query.data.split("_")[3]))  # Обновляем данные состояния с ID канала
    await AuthStates.entering_task_details.set()
    await callback_query.message.answer("Введите детали задачи (название и описание через запятую):")

async def process_task_details(message: types.Message, state: FSMContext):
    task_data = await state.get_data()
    try:
        title, description = message.text.split(",", 1)  # Предполагаем, что название и описание разделены запятой
        db: Database = message.bot['db']
        await db.create_task(channel_id=task_data['channel_id'], title=title.strip(), description=description.strip())
        await message.reply("Задача создана.")
    except ValueError:
        await message.answer("Некорректный формат ввода. Введите название и описание задачи через запятую.")
    except Exception as e:
        await message.answer(f"Произошла ошибка при создании задачи: {e}")

    await moderator_menu(message, state)

def register_handlers(dp: Dispatcher):
    dp.register_callback_query_handler(moderator_menu, lambda c: c.data == 'moderator', state='*')
    dp.register_callback_query_handler(create_story, lambda c: c.data == 'create_story', state=AuthStates.moderator)
    dp.register_message_handler(handle_new_story, content_types=types.ContentTypes.TEXT, state=AuthStates.creating_story)
    dp.register_callback_query_handler(view_tasks, lambda c: c.data == 'view_tasks', state=AuthStates.moderator)
    dp.register_callback_query_handler(review_task, lambda c: c.data.startswith('review_task_'), state=AuthStates.moderator)
    dp.register_callback_query_handler(approve_task, lambda c: c.data.startswith('approve_task_'), state=AuthStates.moderator)
    dp.register_callback_query_handler(revise_task, lambda c: c.data.startswith('revise_task_'), state=AuthStates.moderator)
    dp.register_callback_query_handler(start_task_creation, lambda c: c.data == 'create_story', state=AuthStates.moderator)
    dp.register_callback_query_handler(choose_task_channel, lambda c: c.data.startswith('select_channel_task_'), state=AuthStates.choosing_task_channel)
    dp.register_message_handler(process_task_details, content_types=types.ContentTypes.TEXT, state=AuthStates.entering_task_details)
    dp.register_callback_query_handler(go_back, lambda c: c.data == 'go_back', state='*')