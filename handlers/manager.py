from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from keyboards.manager_buttons import manager_main_keyboard, channel_keyboard, story_keyboard, worker_keyboard, task_approval_keyboard, task_keyboard
from database.database import Database

class ManagerStates(StatesGroup):
    manager = State()
    choosing_channel = State()
    choosing_worker = State()
    entering_task_details = State()
    checking_task = State()
    entering_revision_message = State()

class CreateTask(StatesGroup):
    choosing_channel = State()
    choosing_worker = State()
    entering_task_details = State()

async def manager_menu(message: types.Message, state: FSMContext):
    await message.answer("Меню менеджера:", reply_markup=manager_main_keyboard())
    await ManagerStates.manager.set()

async def start_task_creation(callback_query: types.CallbackQuery, state: FSMContext):
    db: Database = callback_query.message.bot['db']
    channels = await db.get_channels()
    await CreateTask.choosing_channel.set()
    await callback_query.message.answer("Выберите канал:", reply_markup=channel_keyboard(channels))

async def choose_channel(callback_query: types.CallbackQuery, state: FSMContext):
    channel_id = int(callback_query.data.split("_")[1])
    await state.update_data(channel_id=channel_id)
    db: Database = callback_query.message.bot['db']
    workers = await db.get_workers_by_channel(channel_id)
    await CreateTask.choosing_worker.set()
    await callback_query.message.answer("Выберите работника:", reply_markup=worker_keyboard(workers))

async def choose_worker(callback_query: types.CallbackQuery, state: FSMContext):
    worker_id = int(callback_query.data.split("_")[1])
    await state.update_data(worker_id=worker_id)
    await CreateTask.entering_task_details.set()
    await callback_query.message.answer("Введите детали задачи (название и описание):")

async def process_task_details(message: types.Message, state: FSMContext):
    task_data = await state.get_data()
    db: Database = message.bot['db']
    try:
        title, description = message.text.split(",", 1)
        title = title.strip()
        description = description.strip()
        if not title or not description:
            raise ValueError("Некорректный ввод. Оба поля должны быть заполнены.")
    except ValueError as e:
        await message.reply("Пожалуйста, введите название и описание задачи через запятую. Например: 'Название задачи, Описание задачи'")
        return

    worker_id = task_data['worker_id']
    task_id = await db.create_task(channel_id=task_data['channel_id'], title=title, description=description, assigned_to=worker_id, status='assigned')
    if task_id:
        await message.reply(f"Задача создана с ID {task_id}.")
    else:
        await message.reply("Ошибка при создании задачи.")
    await manager_menu(message, state)

async def view_tasks(callback_query: types.CallbackQuery, state: FSMContext):
    db: Database = callback_query.bot['db']
    tasks = await db.get_tasks()
    await callback_query.message.answer("Список всех задач:", reply_markup=task_keyboard(tasks))

async def check_task(callback_query: types.CallbackQuery, state: FSMContext):
    task_id = int(callback_query.data.split("_")[1])
    db: Database = callback_query.message.bot['db']
    task = await db.get_task_details(task_id)

    title = task.get('title', 'Без названия')
    description = task.get('description', 'Без описания')
    file_or_link = task.get('file_or_link', 'Нет прикрепленных файлов или ссылок.')
    worker_name = task.get('worker_name', 'Неизвестный работник')
    channel_name = task.get('channel_name', 'Неизвестный канал')
    revision_message = task.get('revision_message', 'Нет сообщений о доработке')

    await state.update_data(task_id=task_id)
    await callback_query.message.answer(
        f"Детали задачи:\n\n"
        f"Название: {title}\n"
        f"Описание: {description}\n"
        f"Канал: {channel_name}\n"
        f"Работник: {worker_name}\n"
        f"Прикрепленные файлы или ссылки: {file_or_link}\n"
        f"Сообщение о доработке: {revision_message}", 
        reply_markup=task_approval_keyboard(add_back_button=True)
    )
    await ManagerStates.checking_task.set()

async def approve_task(callback_query: types.CallbackQuery, state: FSMContext):
    task_id = int((await state.get_data())['task_id'])
    db: Database = callback_query.bot['db']

    # Получаем информацию о задаче, чтобы узнать worker_id
    task_details = await db.get_task_details(task_id)
    worker_id = task_details['assigned_to']

    # Обновляем статус задачи на "approved"
    await db.update_task_status(task_id, 'approved')

    # Обновляем статистику задач для работника
    await db.update_task_completion(worker_id)

    await callback_query.message.answer("Задача одобрена.")
    await manager_menu(callback_query.message, state)

async def revise_task(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.message.answer("Введите сообщение о доработке:")
    await ManagerStates.entering_revision_message.set()

async def process_revision_message(message: types.Message, state: FSMContext):
    revision_message = message.text
    task_id = int((await state.get_data())['task_id'])
    db: Database = message.bot['db']
    await db.update_task_status(task_id, 'needs_revision')
    await db.update_task_revision_message(task_id, revision_message)
    task_details = await db.get_task_details(task_id)
    await db.add_worker_error(task_details['assigned_to'], f"Revision: {revision_message}")
    await message.answer("Задача отправлена на доработку с сообщением.")
    await manager_menu(message, state)

async def view_stories(callback_query: types.CallbackQuery, state: FSMContext):
    db: Database = callback_query.bot['db']
    stories = await db.get_stories()
    if stories:
        await callback_query.message.answer("Список сценариев:", reply_markup=story_keyboard(stories))
    else:
        await callback_query.message.answer("Нет доступных сценариев.")
    await ManagerStates.manager.set()

async def go_back(callback_query: types.CallbackQuery, state: FSMContext):
    await manager_menu(callback_query.message, state)

def register_handlers(dp: Dispatcher):
    dp.register_message_handler(manager_menu, commands=['manager_menu'], state='*')
    dp.register_callback_query_handler(manager_menu, lambda c: c.data == 'manager_menu', state='*')
    dp.register_callback_query_handler(start_task_creation, lambda c: c.data == 'new_task', state=ManagerStates.manager)
    dp.register_callback_query_handler(view_tasks, lambda c: c.data == 'view_tasks', state=ManagerStates.manager)
    dp.register_callback_query_handler(choose_channel, lambda c: c.data.startswith('channel_'), state=CreateTask.choosing_channel)
    dp.register_callback_query_handler(choose_worker, lambda c: c.data.startswith('worker_'), state=CreateTask.choosing_worker)
    dp.register_message_handler(process_task_details, state=CreateTask.entering_task_details)
    dp.register_callback_query_handler(check_task, lambda c: c.data.startswith('task_'), state=ManagerStates.manager)
    dp.register_callback_query_handler(approve_task, lambda c: c.data == 'approve', state=ManagerStates.checking_task)
    dp.register_callback_query_handler(revise_task, lambda c: c.data == 'revise', state=ManagerStates.checking_task)
    dp.register_message_handler(process_revision_message, state=ManagerStates.entering_revision_message)
    dp.register_callback_query_handler(view_stories, lambda c: c.data == 'view_stories', state=ManagerStates.manager)
    dp.register_callback_query_handler(go_back, lambda c: c.data == 'go_back', state='*')
