from aiogram import Dispatcher, Router
from aiogram.types import Message
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from database.repository import DatabaseRepository
from services.channels import ChannelsService
from services.statistics import StatisticsService
from database import SessionLocal

router = Router()

async def admin_role_required(message: Message, state: FSMContext, db_repository):
    user_data = await state.get_data()
    username = user_data.get('username')
    user = db_repository.get_user_by_username(username)
    
    if not user or not StatisticsService().check_role(user.id, 'Admin'):
        await message.answer("Доступ запрещен: у вас нет прав администратора.")
        return False
    return True

@router.message(Command(commands='create_channel'))
async def create_channel_command(message: Message, state: FSMContext):
    with SessionLocal() as db_session:
        db_repository = DatabaseRepository(db_session)
        if not await admin_role_required(message, state, db_repository):
            return

        args = message.text.split()
        if len(args) != 4:
            await message.answer('Invalid channel creation. Please enter the channel name, link, and manager username in the following format: /create_channel <name> <link> <manager_username>')
            return
        
        name, link, manager_username = args[1], args[2], args[3]
        manager = db_repository.get_user_by_username(manager_username)
        
        if not manager:
            await message.answer('Manager not found. Please provide a valid manager username.')
            return

        channel_service = ChannelsService(db_repository)
        channel = channel_service.create_channel(name, manager.id, link)
        await message.answer(f'Channel "{channel.name}" has been created and user "{manager_username}" has been assigned as the manager.')

@router.message(Command(commands='view_channels'))
async def view_channels_command(message: Message, state: FSMContext):
    with SessionLocal() as db_session:
        db_repository = DatabaseRepository(db_session)
        if not await admin_role_required(message, state, db_repository):
            return

        user_data = await state.get_data()
        username = user_data.get('username')
        admin_user = db_repository.get_user_by_username(username)
        
        channels = ChannelsService(db_repository).get_channels_by_manager_id(admin_user.id)

        if not channels:
            await message.answer('You do not have any channels assigned to you')
            return

        channel_messages = [
            f'{i+1}. {channel.name} (Total expenses: {channel.total_expenses} USD, Total payments: {channel.total_payments} USD)'
            for i, channel in enumerate(channels)
        ]
        await message.answer('\n'.join(channel_messages))

@router.message(Command(commands='statistics'))
async def statistics_command(message: Message, state: FSMContext):
    with SessionLocal() as db_session:
        db_repository = DatabaseRepository(db_session)
        if not await admin_role_required(message, state, db_repository):
            return

        user_data = await state.get_data()
        username = user_data.get('username')
        admin_user = db_repository.get_user_by_username(username)

        channels = ChannelsService(db_repository).get_channels_by_manager_id(admin_user.id)
        total_expenses = sum(channel.total_expenses for channel in channels)
        total_payments = sum(channel.total_payments for channel in channels)

        await message.answer(
            f'You have {len(channels)} channels under your management.\n'
            f'Total expenses for all channels: {total_expenses} USD.\n'
            f'Total payments for all channels: {total_payments} USD.'
        )

def register_handlers(dp: Dispatcher):
    dp.include_router(router)
