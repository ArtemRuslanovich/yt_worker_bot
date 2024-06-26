from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from keyboards.admin_buttons import channel_keyboard, main_admin_keyboard, channel_list_keyboard, worker_list_keyboard, statistics_keyboard
from database.database import Database
from datetime import datetime

class AuthStates(StatesGroup):
    admin = State()
    creating_channel = State()
    choosing_stats_type = State()
    choosing_income_channel = State() 
    entering_income_details = State()  

async def admin_panel(message: types.Message, state: FSMContext):
    await message.answer("Админ панель:", reply_markup=main_admin_keyboard())
    await AuthStates.admin.set()

async def go_back(callback_query: types.CallbackQuery, state: FSMContext):
    await admin_panel(callback_query.message, state)

async def create_channel(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.message.answer("Введите название нового канала:")
    await AuthStates.creating_channel.set()

async def handle_new_channel(message: types.Message, state: FSMContext):
    db: Database = message.bot['db']
    await db.create_channel(message.text)
    await message.answer("Канал создан.")
    await admin_panel(message, state)

async def view_channels(callback_query: types.CallbackQuery, state: FSMContext):
    db: Database = callback_query.bot['db']
    channels = await db.get_channels()
    await callback_query.message.answer("Список каналов:", reply_markup=channel_list_keyboard(channels, add_back_button=True))
    await AuthStates.admin.set()

async def view_workers(callback_query: types.CallbackQuery, state: FSMContext):
    db: Database = callback_query.bot['db']
    workers = await db.get_workers()
    await callback_query.message.answer("Список работников:", reply_markup=worker_list_keyboard(workers, add_back_button=True))
    await AuthStates.admin.set()

async def choose_statistics(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.message.answer("Выберите тип статистики:", reply_markup=statistics_keyboard(add_back_button=True))
    await AuthStates.choosing_stats_type.set()

async def view_statistics(callback_query: types.CallbackQuery, state: FSMContext):
    db: Database = callback_query.bot['db']

    if callback_query.data == "stats_channels":
        stats = await db.get_statistics_by_channels()
        if stats:
            formatted_stats = []
            for record in stats:
                formatted_stats.append(
                    f"Название канала: {record['channel_name']}\n"
                    f"Доход: {record['income']}\n"
                    f"Расход: {record['expense']}\n"
                    f"Чистая прибыль: {record['net_profit']}\n"  # Ensure net_profit is correctly accessed here
                    f"Задания выполнены: {record['tasks_completed']}\n"
                    f"Создано: {record['created_at']}\n"
                    f"Обновлено: {record['updated_at']}\n"
                    "-------------------------"
                )
            message_text = "\n\n".join(formatted_stats)
            await callback_query.message.answer(f"Статистика по каналам:\n\n{message_text}")
        else:
            await callback_query.message.answer("Нет доступной статистики по каналам.")
    elif callback_query.data == "stats_workers":
        stats = await db.get_statistics_by_workers()
        if stats:
            formatted_stats = []
            for record in stats:
                formatted_stats.append(
                    f"Имя работника: {record['worker_username']}\n"
                    f"Задания выполнены: {record['tasks_completed']}\n"
                    f"Ошибки сделаны: {record['errors_made']}\n"
                    f"Сумма затрат: {record['amount_spent']}\n"
                    f"Создано: {record['created_at']}\n"
                    f"Обновлено: {record['updated_at']}\n"
                    "-------------------------"
                )
            message_text = "\n\n".join(formatted_stats)
            await callback_query.message.answer(f"Статистика по работникам:\n\n{message_text}")
        else:
            await callback_query.message.answer("Нет доступной статистики по работникам.")
    await AuthStates.admin.set()

async def start_income_addition(callback_query: types.CallbackQuery, state: FSMContext):
    db: Database = callback_query.message.bot['db']
    channels = await db.get_channels()  # Получение списка каналов из БД
    await AuthStates.choosing_income_channel.set()
    await callback_query.message.answer("Выберите канал:", reply_markup=channel_keyboard(channels, add_back_button=True))

async def choose_income_channel(callback_query: types.CallbackQuery, state: FSMContext):
    await state.update_data(channel_id=int(callback_query.data.split("_")[3]))  # Обновляем данные состояния с ID канала
    await AuthStates.entering_income_details.set()
    await callback_query.message.answer("Введите сумму дохода за текущий месяц:")

async def process_income_details(message: types.Message, state: FSMContext):
    try:
        amount = float(message.text)
        task_data = await state.get_data()
        channel_id = task_data['channel_id']
        db: Database = message.bot['db']
        await db.add_monthly_income_to_channel(channel_id, amount, "Доход за текущий месяц")
        await message.answer(f"Доход в размере {amount} успешно добавлен для канала с ID {channel_id}.")
    except ValueError:
        await message.answer("Некорректный формат ввода. Введите число.")
    except Exception as e:
        await message.answer(f"Произошла ошибка при добавлении дохода: {e}")

    await admin_panel(message, state)

def register_handlers(dp: Dispatcher):
    dp.register_message_handler(admin_panel, commands=['menu'], state='*')
    dp.register_callback_query_handler(admin_panel, lambda c: c.data == 'admin', state='*')
    dp.register_callback_query_handler(create_channel, lambda c: c.data == 'create_channel', state=AuthStates.admin)
    dp.register_message_handler(handle_new_channel, content_types=types.ContentTypes.TEXT, state=AuthStates.creating_channel)
    dp.register_callback_query_handler(view_channels, lambda c: c.data == 'view_channels', state=AuthStates.admin)
    dp.register_callback_query_handler(view_workers, lambda c: c.data == 'view_workers', state=AuthStates.admin)
    dp.register_callback_query_handler(choose_statistics, lambda c: c.data == 'view_statistics', state=AuthStates.admin)
    dp.register_callback_query_handler(view_statistics, lambda c: c.data in ['stats_channels', 'stats_workers'], state=AuthStates.choosing_stats_type)
    dp.register_callback_query_handler(start_income_addition, lambda c: c.data == 'add_monthly_income', state='*')
    dp.register_callback_query_handler(choose_income_channel, lambda c: c.data.startswith('select_channel_income_'), state=AuthStates.choosing_income_channel)
    dp.register_message_handler(process_income_details, content_types=types.ContentTypes.TEXT, state=AuthStates.entering_income_details)
    dp.register_callback_query_handler(go_back, lambda c: c.data == 'go_back', state='*')
