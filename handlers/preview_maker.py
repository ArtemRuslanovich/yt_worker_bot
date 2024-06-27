from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from database.database import Database
from keyboards.preview_maker_buttons import preview_maker_main_keyboard, task_selection_keyboard, task_action_keyboard
from aiogram.dispatcher.filters.state import State, StatesGroup

class PreviewMakerStates(StatesGroup):
    preview_maker = State()
    selecting_task = State()
    awaiting_file_or_link = State()

async def preview_maker_menu(message: types.Message, state: FSMContext):
    await message.answer("Меню создателя предпросмотров:", reply_markup=preview_maker_main_keyboard())
    await PreviewMakerStates.preview_maker.set()

async def view_tasks(callback_query: types.CallbackQuery, state: FSMContext):
    db: Database = callback_query.message.bot['db']
    data = await state.get_data()
    preview_maker_id = data.get('user_id')
    
    if preview_maker_id:
        tasks = await db.get_tasks_by_preview_maker(preview_maker_id)
        print(f"Tasks for preview maker {preview_maker_id}: {tasks}")  # Отладочный вывод
        if tasks:
            await callback_query.message.answer("Список доступных задач:", reply_markup=task_selection_keyboard(tasks, add_back_button=True))
            await PreviewMakerStates.selecting_task.set()
        else:
            await callback_query.message.answer("Нет доступных задач.")
            await PreviewMakerStates.preview_maker.set()
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
    preview_maker_id = data.get('user_id')
    
    if preview_maker_id:
        db: Database = callback_query.message.bot['db']
        task_details = await db.get_task_details(task_id)
        await callback_query.message.answer(f"Детали задачи:\n\nНазвание: {task_details['title']}\nОписание: {task_details['details']}")
        await callback_query.message.answer("Пожалуйста, отправьте файл или ссылку на файл для этой задачи.")
        await state.update_data(task_id=task_id)
        await PreviewMakerStates.awaiting_file_or_link.set()
    else:
        await callback_query.message.answer("Ошибка авторизации. Пожалуйста, войдите снова.")

async def receive_file_or_link(message: types.Message, state: FSMContext):
    data = await state.get_data()
    task_id = data.get('task_id')
    if not task_id:
        await message.answer("Ошибка. Задача не выбрана. Пожалуйста, начните сначала.")
        await PreviewMakerStates.preview_maker.set()
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
    await PreviewMakerStates.preview_maker.set()

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
    await PreviewMakerStates.preview_maker.set()

async def go_back(callback_query: types.CallbackQuery, state: FSMContext):
    await preview_maker_menu(callback_query.message, state)

def register_handlers(dp: Dispatcher):
    dp.register_message_handler(preview_maker_menu, commands=['preview_menu'], state='*')
    dp.register_callback_query_handler(preview_maker_menu, lambda c: c.data == 'preview_menu', state='*')
    dp.register_callback_query_handler(view_tasks, lambda c: c.data == 'view_tasks', state=PreviewMakerStates.preview_maker)
    dp.register_callback_query_handler(select_task, lambda c: c.data.startswith('select_task'), state=PreviewMakerStates.selecting_task)
    dp.register_message_handler(receive_file_or_link, content_types=['document', 'text'], state=PreviewMakerStates.awaiting_file_or_link)
    dp.register_callback_query_handler(send_task_for_review, lambda c: c.data == 'send_review_task', state=PreviewMakerStates.preview_maker)
    dp.register_callback_query_handler(go_back, lambda c: c.data == 'go_back', state='*')
