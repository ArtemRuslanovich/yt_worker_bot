from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from keyboards.shooter_buttons import shooter_main_keyboard, task_selection_keyboard, task_action_keyboard
from database.database import Database
from aiogram.dispatcher.filters.state import State, StatesGroup


class ShooterStates(StatesGroup):
    shooter = State()
    selecting_task = State()
    awaiting_file_or_link = State()

async def shooter_menu(message: types.Message, state: FSMContext):
    await message.answer("Меню оператора:", reply_markup=shooter_main_keyboard())
    await ShooterStates.shooter.set()

async def view_tasks(callback_query: types.CallbackQuery, state: FSMContext):
    db: Database = callback_query.message.bot['db']
    data = await state.get_data()
    shooter_id = data.get('user_id')
    
    if shooter_id:
        tasks = await db.get_tasks_by_shooter(shooter_id)
        print(f"Tasks for shooter {shooter_id}: {tasks}")  # Отладочный вывод
        if tasks:
            await callback_query.message.answer("Список доступных задач:", reply_markup=task_selection_keyboard(tasks))
            await ShooterStates.selecting_task.set()
        else:
            await callback_query.message.answer("Нет доступных задач.")
            await ShooterStates.shooter.set()
    else:
        await callback_query.message.answer("Ошибка авторизации. Пожалуйста, войдите снова.")

async def select_task(callback_query: types.CallbackQuery, state: FSMContext):
    data_parts = callback_query.data.split("_")
    if len(data_parts) < 3:
        await callback_query.message.answer("Неверный формат данных. Пожалуйста, попробуйте снова.")
        return

    try:
        task_id = int(data_parts[2])
    except ValueError:
        await callback_query.message.answer("Некорректный идентификатор задачи. Пожалуйста, попробуйте снова.")
        return

    data = await state.get_data()
    shooter_id = data.get('user_id')
    
    if shooter_id:
        db: Database = callback_query.message.bot['db']
        task_details = await db.get_task_details(task_id)
        await callback_query.message.answer(f"Детали задачи:\n\nНазвание: {task_details['title']}\nОписание: {task_details['details']}")
        await callback_query.message.answer("Пожалуйста, отправьте файл или ссылку на файл для этой задачи.")
        await state.update_data(task_id=task_id)
        await ShooterStates.awaiting_file_or_link.set()
    else:
        await callback_query.message.answer("Ошибка авторизации. Пожалуйста, войдите снова.")

async def receive_file_or_link(message: types.Message, state: FSMContext):
    data = await state.get_data()
    task_id = data.get('task_id')
    if not task_id:
        await message.answer("Ошибка. Задача не выбрана. Пожалуйста, начните сначала.")
        await ShooterStates.shooter.set()
        return

    if message.content_type == 'document':
        file_id = message.document.file_id
        await state.update_data(file_or_link=file_id)
    elif message.content_type == 'text':
        file_link = message.text
        await state.update_data(file_or_link=file_link)
    else:
        await message.answer("Пожалуйста, отправьте либо файл, либо ссылку на файл.")
        return

    await message.answer("Файл или ссылка получены. Теперь вы можете отправить задачу на проверку.", reply_markup=task_action_keyboard(add_back_button=True))
    await ShooterStates.shooter.set()

async def send_task_for_review(callback_query: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    task_id = data.get('task_id')
    file_or_link = data.get('file_or_link')

    if not task_id or not file_or_link:
        await callback_query.message.answer("Ошибка данных. Пожалуйста, начните процесс заново.")
        return

    db: Database = callback_query.message.bot['db']
    await db.update_task_status(task_id, 'pending_review')
    # Сохраните файл или ссылку в базу данных, если это не было сделано ранее

    await callback_query.message.answer("Задача отправлена на проверку.")
    await ShooterStates.shooter.set()

async def go_back(callback_query: types.CallbackQuery, state: FSMContext):
    await shooter_menu(callback_query.message, state)

def register_handlers(dp: Dispatcher):
    dp.register_message_handler(shooter_menu, commands=['shooter_menu'], state='*')
    dp.register_callback_query_handler(view_tasks, lambda c: c.data == 'view_tasks', state=ShooterStates.shooter)
    dp.register_callback_query_handler(select_task, lambda c: c.data.startswith('select_task'), state=ShooterStates.selecting_task)
    dp.register_message_handler(receive_file_or_link, content_types=['document', 'text'], state=ShooterStates.awaiting_file_or_link)
    dp.register_callback_query_handler(send_task_for_review, lambda c: c.data == 'send_review_task', state=ShooterStates.shooter)
    dp.register_callback_query_handler(go_back, lambda c: c.data == 'go_back', state='*')
