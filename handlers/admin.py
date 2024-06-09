from aiogram import Dispatcher, Router
from aiogram.types import Message
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from database.repository import DatabaseRepository
from services.channels import ChannelsService
from services.payment import PaymentService
from services.statistics import StatisticsService
from database import SessionLocal

router = Router()

async def admin_role_required(message: Message, state: FSMContext, db_repository):
    user_data = await state.get_data()
    username = user_data.get('username')
    user = db_repository.get_user_by_username(username)
    
    if not user or not StatisticsService(db_repository).check_role(user.id, 'Admin'):
        await message.answer("Доступ запрещен: у вас нет прав администратора.")
        return False
    return True

@router.message(Command(commands='create_channel'))
async def create_channel_command(message: Message, state: FSMContext):
    with SessionLocal() as db_session:
        db_repository = DatabaseRepository(db_session)
        user_data = await state.get_data()
        if not await admin_role_required(user_data, state, db_repository):
            return

        text = message.text.split()
        name = text[1] if len(text) > 1 else None
        manager_username = text[2] if len(text) > 2 else None
        link = text[3] if len(text) > 3 else None

        if not name or not manager_username or not link:
            await message.answer('Invalid channel creation. Please enter the channel name, manager username, and link in the following format: create_channel <name> <manager_username> <link>')
            return

        manager = db_repository.get_user_by_username(manager_username)
        if not manager:
            await message.answer(f'Manager with username {manager_username} not found.')
            return

        # Проверка на существование канала с таким именем
        existing_channel = db_repository.get_channel_by_name(name)
        if existing_channel:
            await message.answer(f'Channel with name {name} already exists.')
            return

        channel_service = ChannelsService(db_repository)
        channel = channel_service.create_channel(name, manager.id, link)
        await message.answer(f'Channel "{channel.name}" has been created and assigned to manager {manager.username}')

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

        payment_service = PaymentService()

        channel_messages = []
        for i, channel in enumerate(channels):
            total_expenses = db_repository.get_total_expenses_for_channel(channel.id)
            total_payments = payment_service.get_total_payments(channel.id)
            channel_messages.append(
                f'{i+1}. {channel.name} (Total expenses: {total_expenses} USD, Total payments: {total_payments} USD)'
            )

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
        
        payment_service = PaymentService()

        total_expenses = sum(db_repository.get_total_expenses_for_channel(channel.id) for channel in channels)
        total_payments = sum(payment_service.get_total_payments(channel.id) for channel in channels)

        await message.answer(
            f'You have {len(channels)} channels under your management.\n'
            f'Total expenses for all channels: {total_expenses} USD.\n'
            f'Total payments for all channels: {total_payments} USD.'
        )

def register_handlers(dp: Dispatcher):
    dp.include_router(router)