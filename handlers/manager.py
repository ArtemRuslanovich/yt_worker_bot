from aiogram import types, Dispatcher
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from database.database import Database
from keyboards.manager_buttons import channel_keyboard, task_keyboard, task_approval_keyboard

class CreateTask(StatesGroup):
    choosing_channel = State()
    entering_task_details = State()

async def start_task_creation(message: types.Message):
    db = Database()
    channels = await db.get_channels()  # Получение списка каналов из БД
    await CreateTask.choosing_channel.set()
    await message.answer("Выберите канал:", reply_markup=channel_keyboard(channels))

async def choose_channel(callback_query: types.CallbackQuery, state: FSMContext):
    await state.update_data(channel_id=callback_query.data.split("_")[1])
    await CreateTask.next()
    await callback_query.message.answer("Введите детали задачи:")

async def process_task_details(message: types.Message, state: FSMContext):
    task_data = await state.get_data()
    db = Database()
    await db.create_task(channel_id=task_data['channel_id'], details=message.text)
    await message.reply("Задача создана.")
    await state.finish()

async def view_tasks(message: types.Message):
    db = Database()
    tasks = await db.get_tasks()  # Получение всех задач
    await message.answer("Список всех задач:", reply_markup=task_keyboard(tasks))

async def check_task(callback_query: types.CallbackQuery):
    task_id = callback_query.data.split("_")[1]
    db = Database()
    task = await db.get_task_details(task_id)
    await callback_query.message.answer(f"Детали задачи: {task['details']}", reply_markup=task_approval_keyboard())

async def approve_task(callback_query: types.CallbackQuery, state: FSMContext):
    task_id = (await state.get_data())['task_id']
    db = Database()
    await db.update_task_status(task_id, 'approved')
    await callback_query.message.answer("Задача одобрена.")

async def revise_task(callback_query: types.CallbackQuery, state: FSMContext):
    task_id = (await state.get_data())['task_id']
    db = Database()
    await db.update_task_status(task_id, 'needs_revision')
    await callback_query.message.answer("Задача отправлена на доработку.")

def register_handlers(dp: Dispatcher):
    dp.register_message_handler(start_task_creation, commands=['new_task'], state='*')
    dp.register_callback_query_handler(choose_channel, state=CreateTask.choosing_channel)
    dp.register_message_handler(process_task_details, state=CreateTask.entering_task_details)
    dp.register_message_handler(view_tasks, commands=['view_tasks'])
    dp.register_callback_query_handler(check_task, lambda c: c.data.startswith('task_'))
    dp.register_callback_query_handler(approve_task, lambda c: c.data == 'approve', state='*')
    dp.register_callback_query_handler(revise_task, lambda c: c.data == 'revise', state='*')

