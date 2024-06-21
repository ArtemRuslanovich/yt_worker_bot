from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from database.database import Database
from keyboards.shooter_buttons import task_selection_keyboard, task_action_keyboard

class AdminStates(StatesGroup):
    shooter = State()

async def view_tasks(message: types.Message, state: FSMContext):
    db: Database = message.bot['db']
    tasks = await db.get_tasks_by_shooter(message.from_user.id)
    if tasks:
        await message.answer("Список доступных задач:", reply_markup=task_selection_keyboard(tasks))
        await AdminStates.shooter.set()
    else:
        await message.answer("Нет доступных задач.")
        await AdminStates.shooter.set()

async def select_task(callback_query: types.CallbackQuery, state: FSMContext):
    task_id = callback_query.data.split("_")[2]
    db: Database = callback_query.bot['db']
    await db.assign_task_to_shooter(task_id, callback_query.from_user.id)
    await callback_query.message.answer("Задача выбрана для работы.", reply_markup=task_action_keyboard())
    await AdminStates.shooter.set()

async def send_task_for_review(callback_query: types.CallbackQuery, state: FSMContext):
    db: Database = callback_query.bot['db']
    task_id = callback_query.message.text.split()[-1]  # Предполагаем, что ID задачи находится в последнем сообщении
    await db.update_task_status(task_id, 'pending_review')
    await callback_query.message.answer("Задача отправлена на проверку.")
    await AdminStates.shooter.set()

def register_handlers(dp: Dispatcher):
    dp.register_message_handler(view_tasks, commands=['my_tasks'], state=AdminStates.shooter)
    dp.register_callback_query_handler(select_task, lambda c: c.data.startswith('select_task'), state=AdminStates.shooter)
    dp.register_callback_query_handler(send_task_for_review, lambda c: c.data == 'send_review', state=AdminStates.shooter)