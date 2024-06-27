from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from database.database import Database
from keyboards.moderator_buttons import moderator_main_keyboard, review_task_keyboard, task_review_keyboard
from aiogram.dispatcher.filters.state import State, StatesGroup

class ModeratorStates(StatesGroup):
    moderator = State()
    reviewing_task = State()

async def moderator_menu(message: types.Message, state: FSMContext):
    await message.answer("Меню модератора:", reply_markup=moderator_main_keyboard())
    await ModeratorStates.moderator.set()

async def view_review_tasks(callback_query: types.CallbackQuery, state: FSMContext):
    db: Database = callback_query.message.bot['db']
    tasks = await db.get_tasks_for_review()
    await callback_query.message.answer("Список задач на ревью:", reply_markup=review_task_keyboard(tasks, add_back_button=True))

async def review_task(callback_query: types.CallbackQuery, state: FSMContext):
    task_id = int(callback_query.data.split("_")[2])
    db: Database = callback_query.message.bot['db']
    task = await db.get_task_details(task_id)
    await state.update_data(task_id=task_id)
    await callback_query.message.answer(f"Детали задачи: {task['details']}", reply_markup=task_review_keyboard(add_back_button=True))

async def approve_task(callback_query: types.CallbackQuery, state: FSMContext):
    task_id = int((await state.get_data())['task_id'])
    db: Database = callback_query.message.bot['db']
    await db.update_task_status(task_id, 'approved')
    await callback_query.message.answer("Задача одобрена.")
    await moderator_menu(callback_query.message, state)

async def revise_task(callback_query: types.CallbackQuery, state: FSMContext):
    task_id = int((await state.get_data())['task_id'])
    db: Database = callback_query.message.bot['db']
    await db.update_task_status(task_id, 'needs_revision')
    await callback_query.message.answer("Задача отправлена на доработку.")
    await moderator_menu(callback_query.message, state)

async def go_back(callback_query: types.CallbackQuery, state: FSMContext):
    await moderator_menu(callback_query.message, state)

def register_handlers(dp: Dispatcher):
    dp.register_message_handler(moderator_menu, commands=['moderator_menu'], state='*')
    dp.register_callback_query_handler(moderator_menu, lambda c: c.data == 'moderator_menu', state='*')
    dp.register_callback_query_handler(view_review_tasks, lambda c: c.data == 'view_review_tasks', state=ModeratorStates.moderator)
    dp.register_callback_query_handler(review_task, lambda c: c.data.startswith('review_task'), state=ModeratorStates.reviewing_task)
    dp.register_callback_query_handler(approve_task, lambda c: c.data == 'approve', state=ModeratorStates.moderator)
    dp.register_callback_query_handler(revise_task, lambda c: c.data == 'revise', state=ModeratorStates.moderator)
    dp.register_callback_query_handler(go_back, lambda c: c.data == 'go_back', state='*')
