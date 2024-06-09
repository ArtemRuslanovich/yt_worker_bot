import datetime
from aiogram import Dispatcher, Router
from aiogram.types import Message
from aiogram.filters.command import Command
from database.repository import DatabaseRepository
from services.expenses import ExpensesService
from services.statistics import StatisticsService
from services.tasks import TasksService
from database import SessionLocal
from aiogram.fsm.context import FSMContext

router = Router()

async def manager_role_required(message: Message, state: FSMContext, db_repository):
    """Проверка, что пользователь имеет роль 'Manager'."""
    user_data = await state.get_data()
    username = user_data.get('username')
    if not username:
        await message.answer("Ошибка аутентификации. Пожалуйста, войдите в систему.")
        return False

    if not StatisticsService(db_repository).check_role(username, 'Manager'):
        await message.answer("Доступ запрещен: у вас нет прав менеджера.")
        return False
    return True

@router.message(Command(commands='create_task'))
async def create_task_command(message: Message, state: FSMContext):
    with SessionLocal() as db_session:
        db_repository = DatabaseRepository(db_session)
        if not await manager_role_required(message, state, db_repository):
            return

        text = message.text.split()
        title = text[1] if len(text) > 1 else None
        description = text[2] if len(text) > 2 else None
        worker_id = int(text[3]) if len(text) > 3 else None
        deadline = datetime.datetime.strptime(text[4], '%Y-%m-%d') if len(text) > 4 else None
        channel_id = int(text[5]) if len(text) > 5 else None

        if not title or not worker_id or not deadline or not channel_id:
            await message.answer('Invalid task creation. Please enter task information in the correct format.')
            return

        task = TasksService(db_repository).create_task(title, description, worker_id, deadline, channel_id)
        worker = db_repository.get_user_by_id(worker_id)
        await message.answer(f'Task "{task.title}" has been created and assigned to {worker.username}')

@router.message(Command(commands='assign_task'))
async def assign_task_command(message: Message, state: FSMContext):
    with SessionLocal() as db_session:
        db_repository = DatabaseRepository(db_session)
        if not await manager_role_required(message, state, db_repository):
            return

        text = message.text.split()
        task_id = int(text[1]) if len(text) > 1 else None
        worker_id = int(text[2]) if len(text) > 2 else None

        if not task_id or not worker_id:
            await message.answer('Invalid task assignment. Please enter task ID and worker ID in the correct format.')
            return

        if not TasksService(db_repository).assign_task(task_id, worker_id):
            await message.answer('Task assignment failed. Please check task and worker IDs.')
            return

        worker = db_repository.get_user_by_id(worker_id)
        await message.answer(f'Task has been assigned to worker {worker.username}.')

@router.message(Command(commands='log_expense'))
async def log_expense_command(message: Message, state: FSMContext):
    with SessionLocal() as db_session:
        db_repository = DatabaseRepository(db_session)
        if not await manager_role_required(message, state, db_repository):
            return

        text = message.text.split()
        amount = float(text[1]) if len(text) > 1 else None
        currency = text[2] if len(text) > 2 else None
        channel_id = int(text[3]) if len(text) > 3 else None

        if not amount or not currency or not channel_id or (currency not in ['USD', 'RUB']):
            await message.answer('Invalid expense logging. Please enter amount, currency, and channel ID in the correct format.')
            return

        user_data = await state.get_data()
        username = user_data.get('username')
        manager = db_repository.get_user_by_username(username)

        ExpensesService(db_repository).log_expense(manager.id, amount, currency, channel_id)
        await message.answer(f'Expense of {amount} {currency} has been logged for channel ID {channel_id}.')

@router.message(Command(commands='statistics'))
async def statistics_command(message: Message, state: FSMContext):
    with SessionLocal() as db_session:
        db_repository = DatabaseRepository(db_session)
        if not await manager_role_required(message, state, db_repository):
            return

        user_data = await state.get_data()
        username = user_data.get('username')
        manager = db_repository.get_user_by_username(username)

        stats = StatisticsService(db_repository).get_worker_statistics(manager.id)
        await message.answer(
            f'You have completed {stats["on_time"]} tasks on time and missed {stats["missed"]} deadlines.\n'
            f'Total expenses: {stats["total_expenses"]} USD, {stats["total_rub"]} RUB.\n'
            f'Total payments: {stats["total_payments"]} USD.'
        )

def register_handlers(dp: Dispatcher):
    dp.include_router(router)
