from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import Text
from database.database import Database
from keyboards.admin_buttons import channel_list_keyboard, worker_list_keyboard, statistics_keyboard

class AuthStates(StatesGroup):
    admin = State()
    creating_channel = State()
    viewing_statistics = State()

async def admin_panel(message: types.Message, state: FSMContext):
    await message.answer("Админ панель:", reply_markup=statistics_keyboard())
    await AuthStates.admin.set()

async def create_channel(message: types.Message, state: FSMContext):
    await message.answer("Введите название нового канала:")
    await AuthStates.creating_channel.set()

async def handle_new_channel(message: types.Message, state: FSMContext):
    db: Database = message.bot['db']
    await db.create_channel(message.text)
    await message.answer("Канал создан.")
    await AuthStates.admin.set()

async def view_channels(message: types.Message, state: FSMContext):
    db: Database = message.bot['db']
    channels = await db.get_channels()
    await message.answer("Список каналов:", reply_markup=channel_list_keyboard(channels))
    await AuthStates.admin.set()

async def view_workers(message: types.Message, state: FSMContext):
    db: Database = message.bot['db']
    workers = await db.get_workers()
    await message.answer("Список работников:", reply_markup=worker_list_keyboard(workers))
    await AuthStates.admin.set()

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
                    f"Чистая прибыль: {record['net_profit']}\n"
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
    elif callback_query.data == "stats_overall":
        stats = await db.get_overall_statistics()
        if stats:
            record = stats[0]
            message_text = (
                f"Общая статистика по всем каналам:\n\n"
                f"Общий доход: {record['total_income']}\n"
                f"Общий расход: {record['total_expense']}\n"
                f"Общая чистая прибыль: {record['total_net_profit']}\n"
                f"Общее количество выполненных работ: {record['total_tasks_completed']}\n"
                "-------------------------"
            )
            await callback_query.message.answer(message_text)
        else:
            await callback_query.message.answer("Нет доступной общей статистики.")
    await AuthStates.admin.set()

def register_handlers(dp: Dispatcher):
    dp.register_message_handler(admin_panel, commands=['admin'], state='*')
    dp.register_message_handler(create_channel, commands=['create_channel'], state=AuthStates.admin)
    dp.register_message_handler(handle_new_channel, content_types=types.ContentTypes.TEXT, state=AuthStates.creating_channel)
    dp.register_message_handler(view_channels, commands=['view_channels'], state=AuthStates.admin)
    dp.register_message_handler(view_workers, commands=['view_workers'], state=AuthStates.admin)
    dp.register_callback_query_handler(view_statistics, lambda c: c.data in ['stats_channels', 'stats_workers', 'stats_overall'], state=AuthStates.admin)
