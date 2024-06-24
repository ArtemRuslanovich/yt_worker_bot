from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from database.database import Database
from keyboards.editor_buttons import editor_main_keyboard, task_selection_keyboard, task_action_keyboard
from states.auth_states import AuthStates
from aiogram.dispatcher.filters.state import State, StatesGroup

class EditorStates(StatesGroup):
    editor = State()
    selecting_task = State()

async def editor_menu(message: types.Message, state: FSMContext):
    await message.answer("Меню редактора:", reply_markup=editor_main_keyboard())
    await EditorStates.editor.set()

async def view_tasks(callback_query: types.CallbackQuery, state: FSMContext):
    db: Database = callback_query.message.bot['db']
    tasks = await db.get_tasks_by_editor(callback_query.from_user.id)
    if tasks:
        await callback_query.message.answer("Список доступных задач для монтажа:", reply_markup=task_selection_keyboard(tasks, add_back_button=True))
        await EditorStates.selecting_task.set()
    else:
        await callback_query.message.answer("Нет доступных задач.")
        await EditorStates.editor.set()

async def select_task(callback_query: types.CallbackQuery, state: FSMContext):
    task_id = callback_query.data.split("_")[2]
    db: Database = callback_query.message.bot['db']
    await db.assign_task_to_editor(task_id, callback_query.from_user.id)
    await callback_query.message.answer("Задача выбрана для работы.", reply_markup=task_action_keyboard(add_back_button=True))
    await EditorStates.editor.set()

async def send_task_for_review(callback_query: types.CallbackQuery, state: FSMContext):
    db: Database = callback_query.message.bot['db']
    task_id = callback_query.message.text.split()[-1]  # Assuming the task ID is in the last message
    await db.update_task_status(task_id, 'pending_review')
    await callback_query.message.answer("Задача отправлена на проверку.")
    await EditorStates.editor.set()

async def go_back(callback_query: types.CallbackQuery, state: FSMContext):
    await editor_menu(callback_query.message, state)

def register_handlers(dp: Dispatcher):
    dp.register_message_handler(editor_menu, commands=['editor_menu'], state='*')
    dp.register_callback_query_handler(editor_menu, lambda c: c.data == 'editor_menu', state='*')
    dp.register_callback_query_handler(view_tasks, lambda c: c.data == 'view_tasks', state=EditorStates.editor)
    dp.register_callback_query_handler(select_task, lambda c: c.data.startswith('select_task'), state=EditorStates.selecting_task)
    dp.register_callback_query_handler(send_task_for_review, lambda c: c.data == 'send_review', state=EditorStates.editor)
    dp.register_callback_query_handler(go_back, lambda c: c.data == 'go_back', state='*')
