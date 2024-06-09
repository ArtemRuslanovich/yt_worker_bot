from aiogram import Dispatcher, Router
from aiogram.types import Message
from aiogram.filters.command import Command
from database.repository import DatabaseRepository
from services.expenses import ExpensesService
from services.statistics import StatisticsService
from database import SessionLocal

router = Router()

async def moderator_role_required(message: Message, db_repository):
    """Проверка, что пользователь имеет роль 'Moderator'."""
    if not StatisticsService(db_repository).check_role(message.from_user.id, 'Moderator'):
        await message.answer("Доступ запрещен: у вас нет прав модератора.")
        return False
    return True

@router.message(Command(commands='send_message'))
async def send_message_command(message: Message):
    with SessionLocal() as db_session:
        db_repository = DatabaseRepository(db_session)
        if not await moderator_role_required(message, db_repository):
            return

        text = message.text.split(maxsplit=2)
        if len(text) < 3:
            await message.answer('Invalid command. Use /send_message <channel_name> <message>')
            return

        channel_name = text[1]
        message_text = text[2]

        channel = db_repository.get_channel_by_name(channel_name)
        if not channel:
            await message.answer('Channel not found.')
            return

        # Здесь предполагается интеграция с системой отправки сообщений
        # await bot.send_message(channel.telegram_id, message_text)
        await message.answer(f'Message sent to {channel.name}')

@router.message(Command(commands='log_expense'))
async def log_expense_command(message: Message):
    with SessionLocal() as db_session:
        db_repository = DatabaseRepository(db_session)
        if not await moderator_role_required(message, db_repository):
            return

        text = message.text.split()
        amount = float(text[1]) if len(text) > 1 else None
        currency = text[2] if len(text) > 2 else None
        channel_name = text[3] if len(text) > 3 else None

        channel = db_repository.get_channel_by_name(channel_name)

        if not amount or not currency or not channel_name:
            await message.answer('Invalid expense logging. Please enter amount, currency, and channel name in the correct format.')
            return

        ExpensesService(db_repository).log_expense(message.from_user.id, amount, currency, channel.id)
        await message.answer(f'Expense of {amount} {currency} has been logged for channel {channel.name}.')

@router.message(Command(commands='set_salary'))
async def set_salary_command(message: Message):
    with SessionLocal() as db_session:
        db_repository = DatabaseRepository(db_session)
        if not await moderator_role_required(message, db_repository):
            return

        text = message.text.split()
        worker_username = text[1] if len(text) > 1 else None
        amount = float(text[2]) if len(text) > 2 else None

        if not worker_username or not amount:
            await message.answer('Invalid command. Use /set_salary <username> <amount>')
            return

        worker = db_repository.get_user_by_username(worker_username)
        if not worker:
            await message.answer('Worker not found.')
            return

        db_repository.set_worker_salary(worker.id, amount)
        await message.answer(f'Salary for {worker.username} set to {amount} USD per task.')

def register_handlers(dp: Dispatcher):
    dp.include_router(router)