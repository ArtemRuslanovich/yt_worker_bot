from aiogram import types, Dispatcher
from database.database import Database
from keyboards.moderator_buttons import task_list_keyboard, task_review_keyboard

async def create_story(message: types.Message):
    await message.answer("Введите сюжет для новой задачи:")

async def handle_new_story(message: types.Message):
    db = Database()
    await db.create_story(message.text)
    await message.answer("Сюжет создан.")

async def view_tasks(message: types.Message):
    db = Database()
    tasks = await db.get_tasks_for_review()
    await message.answer("Список задач для проверки:", reply_markup=task_list_keyboard(tasks))

async def review_task(callback_query: types.CallbackQuery):
    task_id = callback_query.data.split("_")[2]
    db = Database()
    task = await db.get_task_details(task_id)
    await callback_query.message.answer(f"Детали задачи: {task['details']}", reply_markup=task_review_keyboard())

async def approve_task(callback_query: types.CallbackQuery):
    task_id = callback_query.data.split("_")[2]
    db = Database()
    await db.update_task_status(task_id, 'approved')
    await callback_query.message.answer("Задача одобрена.")

async def revise_task(callback_query: types.CallbackQuery):
    task_id = callback_query.data.split("_")[2]
    db = Database()
    await db.update_task_status(task_id, 'needs_revision')
    await callback_query.message.answer("Задача отправлена на доработку.")

def register_handlers(dp: Dispatcher):
    dp.register_message_handler(create_story, commands=['create_story'], is_moderator=True)
    dp.register_message_handler(handle_new_story, content_types=types.ContentTypes.TEXT, state='*')
    dp.register_message_handler(view_tasks, commands=['view_tasks'], is_moderator=True)
    dp.register_callback_query_handler(review_task, lambda c: c.data.startswith('review_task'))
    dp.register_callback_query_handler(approve_task, lambda c: c.data == 'approve_task')
    dp.register_callback_query_handler(revise_task, lambda c: c.data == 'revise_task')