# handlers/manager.py
from aiogram import Router, Command, Message
from database.repository import DatabaseRepository
from services.expenses import ExpensesService
from services.payment import PaymentService
from services.statistics import StatisticsService
from services.tasks import TasksService
from database import SessionLocal
import datetime

router = Router()

@router.message(Command(commands='create_task'))
async def create_task_command(message: Message):
    # Создание сессии базы данных
    db_session = SessionLocal()
    db_repository = DatabaseRepository(db_session)

    if not StatisticsService(db_repository).check_role(message.from_user.id, 'Manager'):
        db_session.close()
        return

    user = message.from_user
    text = message.text.split()
    title = text[1] if len(text) > 1 else None
    description = text[2] if len(text) > 2 else None
    thumbnail_draft = text[3] if len(text) > 3 else None
    worker_id = int(text[4]) if len(text) > 4 else None
    deadline = datetime.datetime.strptime(text[5], '%Y-%m-%d') if len(text) > 5 else None

    if not title or not worker_id or not deadline:
        await message.answer('Invalid task creation. Please enter task information in the following format: create_task <title> <description> <thumbnail_draft> <worker_id> <deadline>')
        db_session.close()
        return

    task = TasksService(db_repository).create_task(title, description, thumbnail_draft, worker_id, deadline)
    await message.answer(f'Task "{task.title}" has been created and assigned to {task.worker.username}')
    db_session.close()

@router.message(Command(commands='assign_task'))
async def assign_task_command(message: Message):
    # Создание сессии базы данных
    db_session = SessionLocal()
    db_repository = DatabaseRepository(db_session)

    if not StatisticsService(db_repository).check_role(message.from_user.id, 'Manager'):
        db_session.close()
        return

    user = message.from_user
    text = message.text.split()
    task_id = int(text[1]) if len(text) > 1 else None
    worker_id = int(text[2]) if len(text) > 2 else None

    if not task_id or not worker_id:
        await message.answer('Invalid task assignment. Please enter task ID and worker ID in the following format: assign_task <task_id> <worker_id>')
        db_session.close()
        return

    task = TasksService(db_repository).get_task_by_id(task_id)

    if not task or task.status == 'completed':
        await message.answer('Invalid task assignment. Task with provided ID does not exist or is already completed')
        db_session.close()
        return

    TasksService(db_repository).assign_task(task_id, worker_id)
    await message.answer(f'Task "{task.title}" has been assigned to {task.worker.username}')
    db_session.close()

@router.message(Command(commands='log_expense'))
async def log_expense_command(message: Message):
    # Создание сессии базы данных
    db_session = SessionLocal()
    db_repository = DatabaseRepository(db_session)

    if not StatisticsService(db_repository).check_role(message.from_user.id, 'Manager'):
        db_session.close()
        return

    user = message.from_user
    text = message.text.split()
    amount = float(text[1]) if len(text) > 1 else None
    currency = text[2] if len(text) > 2 else None

    if not amount or not currency or (currency != 'USD' and currency != 'RUB'):
        await message.answer('Invalid expense logging. Please enter amount and currency in the following format: log_expense <amount> <currency (USD or RUB)>')
        db_session.close()
        return

    ExpensesService(db_repository).log_expense(user.id, amount, currency)
    await message.answer(f'Expense of {amount} {currency} has been logged')
    db_session.close()

@router.message(Command(commands='statistics'))
async def statistics_command(message: Message):
    # Создание сессии базы данных
    db_session = SessionLocal()
    db_repository = DatabaseRepository(db_session)

    if not StatisticsService(db_repository).check_role(message.from_user.id, 'Manager'):
        db_session.close()
        return

    user = message.from_user
    on_time, missed = StatisticsService(db_repository).get_worker_statistics(user.id)
    total_usd, total_rub = ExpensesService(db_repository).get_total_expenses(user.id)
    total_payments = PaymentService(db_repository).get_total_payments(user.id)

    await message.answer(
        f'You have completed {on_time} tasks on time and missed {missed} deadlines.\n'
        f'Total expenses: {total_usd} USD, {total_rub} RUB.\n'
        f'Total payments: {total_payments} USD.'
    )
    db_session.close()
