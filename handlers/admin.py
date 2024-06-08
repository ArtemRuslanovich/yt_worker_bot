# handlers/admin.py
from aiogram import Router, Command, Message
from database.repository import DatabaseRepository
from services.channels import ChannelsService
from services.expenses import ExpensesService
from services.payment import PaymentService
from services.statistics import StatisticsService
from database import SessionLocal

router = Router()

@router.message(Command(commands='create_channel'))
async def create_channel_command(message: Message):
    # Создание сессии базы данных
    db_session = SessionLocal()
    db_repository = DatabaseRepository(db_session)

    if not StatisticsService(db_repository).check_role(message.from_user.id, 'Admin'):
        db_session.close()
        return

    user = message.from_user
    name = message.text.split()[1]

    if not name:
        await message.answer('Invalid channel creation. Please enter the channel name in the following format: create_channel <name>')
        db_session.close()
        return

    channel = ChannelsService(db_repository).create_channel(name, user.id)
    await message.answer(f'Channel "{channel.name}" has been created and you have been assigned as the manager')
    db_session.close()

@router.message(Command(commands='view_channels'))
async def view_channels_command(message: Message):
    # Создание сессии базы данных
    db_session = SessionLocal()
    db_repository = DatabaseRepository(db_session)

    if not StatisticsService(db_repository).check_role(message.from_user.id, 'Admin'):
        db_session.close()
        return

    user = message.from_user
    channels = ChannelsService(db_repository).get_channels_by_manager_id(user.id)

    if not channels:
        await message.answer('You do not have any channels assigned to you')
        db_session.close()
        return

    channel_messages = [f'{i+1}. {channel.name} (Total expenses: {channel.total_expenses} USD, Total payments: {channel.total_payments} USD)' for i, channel in enumerate(channels)]
    await message.answer('\n'.join(channel_messages))
    db_session.close()

@router.message(Command(commands='statistics'))
async def statistics_command(message: Message):
    # Создание сессии базы данных
    db_session = SessionLocal()
    db_repository = DatabaseRepository(db_session)

    if not StatisticsService(db_repository).check_role(message.from_user.id, 'Admin'):
        db_session.close()
        return

    user = message.from_user
    channels = ChannelsService(db_repository).get_channels_by_manager_id(user.id)
    total_expenses = 0
    total_payments = 0

    for channel in channels:
        total_expenses += channel.total_expenses
        total_payments += channel.total_payments

    await message.answer(
        f'You have {len(channels)} channels under your management.\n'
        f'Total expenses for all channels: {total_expenses} USD.\n'
        f'Total payments for all channels: {total_payments} USD.'
    )
    db_session.close()

@router.message(Command(commands='log_expense'))
async def log_expense_command(message: Message):
    # Создание сессии базы данных
    db_session = SessionLocal()
    db_repository = DatabaseRepository(db_session)

    if not StatisticsService(db_repository).check_role(message.from_user.id, 'Admin'):
        db_session.close()
        return

    user = message.from_user
    text = message.text.split()
    amount = float(text[1]) if len(text) > 1 else None
    description = text[2] if len(text) > 2 else None
    channel_id = int(text[3]) if len(text) > 3 else user.channel_id

    if not amount or (amount <= 0) or not description:
        await message.answer('Invalid expense logging. Please enter the amount, description, and channel ID in the following format: log_expense <amount> <description> [<channel_id>]')
        db_session.close()
        return

    expense = ExpensesService(db_repository).log_expense(user.id, amount, description, channel_id)
    await message.answer(f'Expense of {amount} USD for "{description}" has been logged for channel {expense.channel.name}')
    db_session.close()

@router.message(Command(commands='log_payment'))
async def log_payment_command(message: Message):
    # Создание сессии базы данных
    db_session = SessionLocal()
    db_repository = DatabaseRepository(db_session)

    if not StatisticsService(db_repository).check_role(message.from_user.id, 'Admin'):
        db_session.close()
        return

    user = message.from_user
    text = message.text.split()
    amount = float(text[1]) if len(text) > 1 else None
    description = text[2] if len(text) > 2 else None
    channel_id = int(text[3]) if len(text) > 3 else user.channel_id

    if not amount or (amount <= 0) or not description:
        await message.answer('Invalid payment logging. Please enter the amount, description, and channel ID in the following format: log_payment <amount> <description> [<channel_id>]')
        db_session.close()
        return

    payment = PaymentService(db_repository).log_payment(user.id, amount, description, channel_id)
    await message.answer(f'Payment of {amount} USD for "{description}" has been logged for channel {payment.channel.name}')
    db_session.close()
