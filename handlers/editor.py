from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from database.database import Database
from keyboards.editor_buttons import task_selection_keyboard, task_action_keyboard

class AuthStates(StatesGroup):
    editor = State()
    selecting_task = State()

async def view_tasks(message: types.Message, state: FSMContext):
    db: Database = message.bot['db']
    tasks = await db.get_tasks_by_editor(message.from_user.id)
    if tasks:
        await message.answer("Список доступных задач для монтажа:", reply_markup=task_selection_keyboard(tasks))
        await AuthStates.selecting_task.set()
    else:
        await message.answer("Нет доступных задач.")
        await AuthStates.editor.set()

async def select_task(callback_query: types.CallbackQuery, state: FSMContext):
    task_id = callback_query.data.split("_")[2]
    db: Database = callback_query.bot['db']
    await db.assign_task_to_editor(task_id, callback_query.from_user.id)
    await callback_query.message.answer("Задача выбрана для работы.", reply_markup=task_action_keyboard())
    await AuthStates.editor.set()

async def send_task_for_review(callback_query: types.CallbackQuery, state: FSMContext):
    db: Database = callback_query.bot['db']
    task_id = callback_query.message.text.split()[-1]  # Предполагаем, что ID задачи находится в последнем сообщении
    await db.update_task_status(task_id, 'pending_review')
    await callback_query.message.answer("Задача отправлена на проверку.")
    await AuthStates.editor.set()

def register_handlers(dp: Dispatcher):
    dp.register_message_handler(view_tasks, commands=['my_tasks'], state=AuthStates.editor)
    dp.register_callback_query_handler(select_task, lambda c: c.data.startswith('select_task'), state=AuthStates.selecting_task)
    dp.register_callback_query_handler(send_task_for_review, lambda c: c.data == 'send_review', state=AuthStates.editor)
