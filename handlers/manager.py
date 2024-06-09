import datetime
from aiogram import Dispatcher, Router
from aiogram.types import Message
from aiogram.filters.command import Command
from database.repository import DatabaseRepository
from services.tasks import TasksService
from services.expenses import ExpensesService
from services.statistics import StatisticsService
from database import SessionLocal

router = Router()

async def manager_role_required(message: Message, db_repository):
    """Проверка, что пользователь имеет роль 'Manager'."""
    if not StatisticsService(db_repository).check_role(message.from_user.id, 'Manager'):
        await message.answer("Доступ запрещен: у вас нет прав менеджера.")
        return False
    return True

@router.message(Command(commands='create_task'))
async def create_task_command(message: Message):
    with SessionLocal() as db_session:
        db_repository = DatabaseRepository(db_session)
        if not await manager_role_required(message, db_repository):
            return

        text = message.text.split()
        title = text[1] if len(text) > 1 else None
        description = text[2] if len(text) > 2 else None
        thumbnail_draft = text[3] if len(text) > 3 else None
        worker_username = text[4] if len(text) > 4 else None
        deadline = datetime.datetime.strptime(text[5], '%Y-%m-%d') if len(text) > 5 else None
        channel_name = text[6] if len(text) > 6 else None

        if not title or not worker_username or not deadline or not channel_name:
            await message.answer('Invalid task creation. Please enter task information in the correct format.')
            return

        worker = db_repository.get_user_by_username(worker_username)
        channel = db_repository.get_channel_by_name(channel_name)

        if not worker or not channel:
            await message.answer('Worker or channel not found.')
            return

        task = TasksService(db_repository).create_task(title, description, thumbnail_draft, worker.id, deadline, channel.id)
        await message.answer(f'Task "{task.title}" has been created and assigned to {worker.username} for channel {channel.name}.')

@router.message(Command(commands='assign_task'))
async def assign_task_command(message: Message):
    with SessionLocal() as db_session:
        db_repository = DatabaseRepository(db_session)
        if not await manager_role_required(message, db_repository):
            return

        text = message.text.split()
        task_id = int(text[1]) if len(text) > 1 else None
        worker_username = text[2] if len(text) > 2 else None

        if not task_id or not worker_username:
            await message.answer('Invalid task assignment. Please enter task ID and worker username in the correct format.')
            return

        worker = db_repository.get_user_by_username(worker_username)

        if not worker:
            await message.answer('Worker not found.')
            return

        if not TasksService(db_repository).assign_task(task_id, worker.id):
            await message.answer('Task assignment failed. Please check task and worker IDs.')
            return

        await message.answer(f'Task has been assigned to {worker.username}.')

@router.message(Command(commands='log_expense'))
async def log_expense_command(message: Message):
    with SessionLocal() as db_session:
        db_repository = DatabaseRepository(db_session)
        if not await manager_role_required(message, db_repository):
            return

        text = message.text.split()
        amount = float(text[1]) if len(text) > 1 else None
        currency = text[2] if len(text) > 2 else None
        channel_name = text[3] if len(text) > 3 else None

        if not amount or not currency or (currency not in ['USD', 'RUB']) or not channel_name:
            await message.answer('Invalid expense logging. Please enter amount, currency, and channel name in the correct format.')
            return

        channel = db_repository.get_channel_by_name(channel_name)

        if not channel:
            await message.answer('Channel not found.')
            return

        ExpensesService(db_repository).log_expense(message.from_user.id, amount, currency, channel.id)
        await message.answer(f'Expense of {amount} {currency} has been logged for channel {channel.name}.')

@router.message(Command(commands='statistics'))
async def statistics_command(message: Message):
    with SessionLocal() as db_session:
        db_repository = DatabaseRepository(db_session)
        if not await manager_role_required(message, db_repository):
            return

        stats = StatisticsService(db_repository).get_worker_statistics(message.from_user.id)
        await message.answer(
            f'You have completed {stats["on_time"]} tasks on time and missed {stats["missed"]} deadlines.\n'
            f'Total expenses: {stats["total_expenses"]} USD, {stats["total_rub"]} RUB.\n'
            f'Total payments: {stats["total_payments"]} USD.'
        )

def register_handlers(dp: Dispatcher):
    dp.include_router(router)