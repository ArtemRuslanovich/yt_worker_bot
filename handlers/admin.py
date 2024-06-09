from aiogram import Dispatcher, Router
from aiogram.types import Message
from aiogram.filters.command import Command
from database.repository import DatabaseRepository
from middlewares.authentication import Authenticator
from services.channels import ChannelsService
from services.payment import PaymentService
from database import SessionLocal
from aiogram.fsm.context import FSMContext
import logging

router = Router()

async def admin_role_required(message: Message, state: FSMContext, db_repository):
    user_data = await state.get_data()
    logging.info(f"State user data: {user_data}")  # Отладочное сообщение
    username = user_data.get('username')
    role = user_data.get('role')
    authenticator = Authenticator(db_repository)

    user = db_repository.get_user_by_username(username)

    logging.info(f"Checking role for user: {user}")  # Отладочное сообщение
    if not user or not authenticator.check_role(user, 'Admin'):
        await message.answer("Access denied: you do not have admin rights.")
        return False
    return True

@router.message(Command(commands='create_channel'))
async def create_channel_command(message: Message, state: FSMContext):
    with SessionLocal() as db_session:
        db_repository = DatabaseRepository(db_session)
        if not await admin_role_required(message, state, db_repository):
            return

        text = message.text.split()
        name = text[1] if len(text) > 1 else None
        link = text[2] if len(text) > 2 else None
        manager_username = text[3] if len(text) > 3 else None

        if not name or not link or not manager_username:
            await message.answer('Invalid channel creation. Please enter the channel information in the correct format.')
            return

        manager = db_repository.get_user_by_username(manager_username)
        if not manager:
            await message.answer('Manager not found.')
            return

        channel_service = ChannelsService(db_repository)
        existing_channel = channel_service.get_channel_by_name(name)
        if existing_channel:
            await message.answer('Channel with this name already exists.')
            return

        channel = channel_service.create_channel(name, manager.id, link)
        await message.answer(f'Channel "{channel.name}" has been created and assigned to {manager.username}')

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

@router.message(Command(commands='send_message'))
async def send_message_command(message: Message, state: FSMContext, db_repository):
    if not await admin_role_required(message, state, db_repository):
        return

    args = message.text.split(maxsplit=3)
    if len(args) < 4:
        await message.answer("Usage: /send_message <channel_name> <message>")
        return

    channel_name, channel_message = args[1], args[2:]
    channel = db_repository.get_channel_by_name(channel_name)
    if not channel:
        await message.answer("Channel not found.")
        return

    # Симулируем отправку сообщения в канал (здесь должен быть реальный вызов API или бота)
    await message.answer(f"Message sent to {channel.name}: '{channel_message}'")

@router.message(Command(commands='view_content_statistics'))
async def view_content_statistics_command(message: Message, state: FSMContext, db_repository):
    if not await admin_role_required(message, state, db_repository):
        return

    stats = db_repository.get_monthly_content_statistics()  # Предположим, что такой метод есть в репозитории
    await message.answer(
        f"Monthly content statistics:\n"
        f"Videos created: {stats['videos_created']}\n"
        f"Previews created: {stats['previews_created']}"
    )

@router.message(Command(commands='add_expense'))
async def add_expense_command(message: Message, state: FSMContext, db_repository):
    if not await admin_role_required(message, state, db_repository):
        return

    args = message.text.split(maxsplit=4)
    if len(args) < 5:
        await message.answer("Usage: /add_expense <channel_name> <amount> <currency>")
        return

    channel_name, amount, currency = args[1], float(args[2]), args[3]
    channel = db_repository.get_channel_by_name(channel_name)
    if not channel:
        await message.answer("Channel not found.")
        return

    db_repository.add_expense(channel.id, amount, currency)
    await message.answer(f"Added {amount} {currency} expense to {channel.name}.")

@router.message(Command(commands='set_bonus'))
async def set_bonus_command(message: Message, state: FSMContext, db_repository):
    if not await admin_role_required(message, state, db_repository):
        return

    args = message.text.split()
    if len(args) < 2:
        await message.answer("Usage: /set_bonus <percentage>")
        return

    percentage = float(args[1])
    db_repository.set_bonus_percentage(percentage)
    await message.answer(f"Bonus percentage set to {percentage}%.")

def register_handlers(dp: Dispatcher):
    dp.include_router(router)