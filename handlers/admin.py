from aiogram import types, Dispatcher
from database.database import Database
from keyboards.admin_buttons import channel_list_keyboard, worker_list_keyboard, statistics_keyboard

async def admin_panel(message: types.Message):
    await message.answer("Админ панель:", reply_markup=statistics_keyboard())

async def create_channel(message: types.Message):
    # Запрашиваем название канала
    await message.answer("Введите название нового канала:")

async def handle_new_channel(message: types.Message):
    db = Database()
    await db.create_channel(message.text)
    await message.answer("Канал создан.")

async def view_channels(message: types.Message):
    db = Database()
    channels = await db.get_channels()
    await message.answer("Список каналов:", reply_markup=channel_list_keyboard(channels))

async def view_workers(message: types.Message):
    db = Database()
    workers = await db.get_workers()
    await message.answer("Список работников:", reply_markup=worker_list_keyboard(workers))

async def view_statistics(callback_query: types.CallbackQuery):
    db = Database()
    if callback_query.data == "stats_channels":
        stats = await db.get_statistics_by_channels()
        await callback_query.message.answer(f"Статистика по каналам: {stats}")
    elif callback_query.data == "stats_workers":
        stats = await db.get_statistics_by_workers()
        await callback_query.message.answer(f"Статистика по работникам: {stats}")

def register_handlers(dp: Dispatcher):
    dp.register_message_handler(admin_panel, commands=['admin'], is_admin=True)
    dp.register_message_handler(create_channel, commands=['create_channel'], is_admin=True)
    dp.register_message_handler(handle_new_channel, content_types=types.ContentTypes.TEXT, state='*')
    dp.register_message_handler(view_channels, commands=['view_channels'], is_admin=True)
    dp.register_message_handler(view_workers, commands=['view_workers'], is_admin=True)
    dp.register_callback_query_handler(view_statistics, lambda c: c.data in ['stats_channels', 'stats_workers'])
