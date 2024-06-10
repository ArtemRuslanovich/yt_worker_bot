import logging
from aiogram import Dispatcher, Router, types
from aiogram.filters.command import Command
from database.repository import DatabaseRepository
from database import SessionLocal
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from middlewares.authentication import Authenticator
from services.statistics import StatisticsService
from services.channels import ChannelsService

router = Router()

class ChannelCreation(StatesGroup):
    waiting_for_name = State()

async def admin_role_required(message: types.Message, state: FSMContext, db_repository):
    user_data = await state.get_data()
    logging.info(f"State user data: {user_data}")
    username = user_data.get('username')
    role = user_data.get('role')
    authenticator = Authenticator(db_repository)

    user = db_repository.get_user_by_username(username)

    logging.info(f"Checking role for user: {user}")
    if not user or not authenticator.check_role(user, 'Admin'):
        await message.answer("Access denied: you do not have admin rights.")
        return False
    return True

@router.message(Command(commands='view_statistics'))
async def view_statistics_command(message: types.Message, state: FSMContext):
    with SessionLocal() as db_session:
        db_repository = DatabaseRepository(db_session)
        if not await admin_role_required(message, state, db_repository):
            return

        statistics_service = StatisticsService(db_repository)
        statistics = statistics_service.get_statistics()

        response = "Статистика:\n\n"
        for channel_stats in statistics['channels']:
            response += f"Канал: {channel_stats['name']}\n"
            response += f"Расходы: {channel_stats['expenses']}\n"
            response += f"Зарплаты: {channel_stats['salaries']}\n"
            response += "\n"
        
        for worker_stats in statistics['workers']:
            response += f"Работник: {worker_stats['username']}\n"
            response += f"Расходы: {worker_stats['expenses']}\n"
            response += f"Зарплата: {worker_stats['salary']}\n"
            response += "\n"

        await message.answer(response)

@router.message(Command(commands='create_channel'))
async def create_channel_command(message: types.Message, state: FSMContext):
    with SessionLocal() as db_session:
        db_repository = DatabaseRepository(db_session)
        if not await admin_role_required(message, state, db_repository):
            return

        await message.answer("Введите название канала:")
        await state.set_state(ChannelCreation.waiting_for_name)

@router.message(ChannelCreation.waiting_for_name)
async def process_channel_name(message: types.Message, state: FSMContext):
    channel_name = message.text

    with SessionLocal() as db_session:
        db_repository = DatabaseRepository(db_session)
        existing_channel = db_repository.get_channel_by_name(channel_name)
        if existing_channel:
            await message.answer("Канал с таким названием уже существует.")
            return

        new_channel = db_repository.create_channel(name=channel_name)
        await message.answer(f"Канал '{new_channel.name}' создан.")
        await state.clear()

@router.message(Command(commands='view_channels'))
async def view_channels_command(message: types.Message, state: FSMContext):
    with SessionLocal() as db_session:
        db_repository = DatabaseRepository(db_session)
        if not await admin_role_required(message, state, db_repository):
            return

        channels_service = ChannelsService(db_repository)
        channels = channels_service.get_all_channels()

        response = "Текущие каналы:\n\n"
        for channel in channels:
            response += f"ID: {channel.id}, Название: {channel.name}\n"

        await message.answer(response)

def register_handlers(dp: Dispatcher):
    dp.include_router(router)