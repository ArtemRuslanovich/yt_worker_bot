from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from keyboards.manager_buttons import manager_main_keyboard, channel_keyboard, task_keyboard, task_approval_keyboard
from database.database import Database

class AuthStates(StatesGroup):
    manager = State()

class CreateTask(StatesGroup):
    choosing_channel = State()
    entering_task_details = State()

async def manager_menu(message: types.Message, state: FSMContext):
    await message.answer("Меню менеджера:", reply_markup=manager_main_keyboard())
    await AuthStates.manager.set()

async def start_task_creation(callback_query: types.CallbackQuery, state: FSMContext):
    db: Database = callback_query.message.bot['db']
    channels = await db.get_channels()  # Получение списка каналов из БД
    await CreateTask.choosing_channel.set()
    await callback_query.message.answer("Выберите канал:", reply_markup=channel_keyboard(channels, add_back_button=True))

async def choose_channel(callback_query: types.CallbackQuery, state: FSMContext):
    await state.update_data(channel_id=int(callback_query.data.split("_")[1]))
    await CreateTask.entering_task_details.set()
    await callback_query.message.answer("Введите детали задачи (название и описание через запятую):")

async def process_task_details(message: types.Message, state: FSMContext):
    task_data = await state.get_data()
    db: Database = message.bot['db']
    title, description = message.text.split(",", 1)  # Предполагаем, что название и описание разделены запятой
    await db.create_task(channel_id=task_data['channel_id'], title=title.strip(), description=description.strip())
    await message.reply("Задача создана.")
    await manager_menu(message, state)

async def view_tasks(callback_query: types.CallbackQuery, state: FSMContext):
    db: Database = callback_query.bot['db']
    tasks = await db.get_tasks()  # Получение всех задач
    await callback_query.message.answer("Список всех задач:", reply_markup=task_keyboard(tasks, add_back_button=True))

async def check_task(callback_query: types.CallbackQuery, state: FSMContext):
    task_id = int(callback_query.data.split("_")[1])
    db: Database = callback_query.bot['db']
    task = await db.get_task_details(task_id)
    await state.update_data(task_id=task_id)
    await callback_query.message.answer(f"Детали задачи: {task['details']}", reply_markup=task_approval_keyboard(add_back_button=True))

async def approve_task(callback_query: types.CallbackQuery, state: FSMContext):
    task_id = int((await state.get_data())['task_id'])
    db: Database = callback_query.bot['db']
    await db.update_task_status(task_id, 'approved')
    await callback_query.message.answer("Задача одобрена.")
    await manager_menu(callback_query.message, state)

async def revise_task(callback_query: types.CallbackQuery, state: FSMContext):
    task_id = int((await state.get_data())['task_id'])
    db: Database = callback_query.bot['db']
    await db.update_task_status(task_id, 'needs_revision')
    await callback_query.message.answer("Задача отправлена на доработку.")
    await manager_menu(callback_query.message, state)

async def go_back(callback_query: types.CallbackQuery, state: FSMContext):
    await manager_menu(callback_query.message, state)

def register_handlers(dp: Dispatcher):
    dp.register_message_handler(manager_menu, commands=['manager_menu'], state='*')
    dp.register_callback_query_handler(manager_menu, lambda c: c.data == 'manager_menu', state='*')
    dp.register_callback_query_handler(start_task_creation, lambda c: c.data == 'new_task', state=AuthStates.manager)
    dp.register_callback_query_handler(view_tasks, lambda c: c.data == 'view_tasks', state=AuthStates.manager)
    dp.register_callback_query_handler(choose_channel, lambda c: c.data.startswith('channel_'), state=CreateTask.choosing_channel)
    dp.register_message_handler(process_task_details, state=CreateTask.entering_task_details)
    dp.register_callback_query_handler(check_task, lambda c: c.data.startswith('task_'), state=AuthStates.manager)
    dp.register_callback_query_handler(approve_task, lambda c: c.data == 'approve', state=AuthStates.manager)
    dp.register_callback_query_handler(revise_task, lambda c: c.data == 'revise', state=AuthStates.manager)
    dp.register_callback_query_handler(go_back, lambda c: c.data == 'go_back', state='*')

