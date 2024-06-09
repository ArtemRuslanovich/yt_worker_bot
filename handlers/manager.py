import datetime
import shlex
from aiogram import Dispatcher, Router
from aiogram.types import Message
from aiogram.filters.command import Command
from database.repository import DatabaseRepository
from middlewares.authentication import Authenticator
from services.expenses import ExpensesService
from services.tasks import TasksService
from services.statistics import StatisticsService
from database import SessionLocal
from aiogram.fsm.context import FSMContext
import logging

router = Router()

async def manager_role_required(message: Message, state: FSMContext, db_repository):
    user_data = await state.get_data()
    logging.info(f"State user data: {user_data}")  # Отладочное сообщение
    username = user_data.get('username')
    role = user_data.get('role')
    authenticator = Authenticator(db_repository)

    user = db_repository.get_user_by_username(username)

    logging.info(f"Checking role for user: {user}")  # Отладочное сообщение
    if not user or not authenticator.check_role(user, 'Manager'):
        await message.answer("Access denied: you do not have manager rights.")
        return False
    return True

@router.message(Command(commands='create_task'))
async def create_task_command(message: Message, state: FSMContext):
    with SessionLocal() as db_session:
        db_repository = DatabaseRepository(db_session)
        if not await manager_role_required(message, state, db_repository):
            return

        args = shlex.split(message.text)
        if len(args) != 6:
            await message.answer('Invalid task creation. Please use the format: /create_task "title" "description" username deadline channel_name')
            return

        title, description, worker_username, deadline_str, channel_name = args[1:]

        try:
            deadline = datetime.datetime.strptime(deadline_str, '%Y-%m-%d')
        except ValueError:
            await message.answer('Invalid date format. Please use YYYY-MM-DD.')
            return

        worker = db_repository.get_user_by_username(worker_username)
        channel = db_repository.get_channel_by_name(channel_name)

        if not worker or not channel:
            await message.answer('Worker or channel not found.')
            return

        status = "pending"  # Статус устанавливается автоматически как "pending"
        task = TasksService(db_repository).create_task(worker.id, title, description, deadline, status, channel.id)
        await message.answer(f'Task "{task.title}" has been created and assigned to {worker.username} in channel {channel.name}.')

@router.message(Command(commands='log_expense'))
async def log_expense_command(message: Message, state: FSMContext):
    user_data = await state.get_data()
    username = user_data.get('username')
    with SessionLocal() as db_session:
        db_repository = DatabaseRepository(db_session)
        if not await manager_role_required(message, state, db_repository):
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

        ExpensesService(db_repository).log_expense(username, amount, currency, channel.id)
        await message.answer(f'Expense of {amount} {currency} has been logged for channel {channel.name}.')

@router.message(Command(commands='statistics'))
async def statistics_command(message: Message, state: FSMContext):
    with SessionLocal() as db_session:
        db_repository = DatabaseRepository(db_session)
        if not await manager_role_required(message, state, db_repository):
            return

        stats = StatisticsService(db_repository).get_worker_statistics(message.from_user.id)
        await message.answer(
            f'You have completed {stats["on_time"]} tasks on time and missed {stats["missed"]} deadlines.\n'
            f'Total expenses: {stats["total_expenses"]} USD, {stats["total_rub"]} RUB.\n'
            f'Total payments: {stats["total_payments"]} USD.'
        )

def register_handlers(dp: Dispatcher):
    dp.include_router(router)