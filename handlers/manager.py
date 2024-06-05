from aiogram import types, dp
from services import *
from services.expenses import ExpensesService
from services.payment import PaymentService
import datetime

from services.statistics import StatisticsService
from services.tasks import TasksService


@dp.message_handler(lambda message: message.text.startswith('create_task') and StatisticsService.check_role(message.from_user, 'Manager'))
async def create_task_command(message: types.Message):
    user = message.from_user
    title = message.text.split()[1]
    description = message.text.split()[2] if len(message.text.split()) > 2 else None
    thumbnail_draft = message.text.split()[3] if len(message.text.split()) > 3 else None
    worker_id = int(message.text.split()[4]) if len(message.text.split()) > 4 else None
    deadline = datetime.strptime(message.text.split()[5], '%Y-%m-%d') if len(message.text.split()) > 5 else None

    if not title or not worker_id or not deadline:
        await message.answer('Invalid task creation. Please enter the task details in the following format: create_task <title> <description> <thumbnail_draft> <worker_id> <deadline>')
        return

    task = TasksService.create_task(title, description, thumbnail_draft, worker_id, deadline, deadline)
    await message.answer(f'Task "{task.title}" has been created and assigned to worker {task.worker.username}')

@dp.message_handler(lambda message: message.text.startswith('assign_task') and StatisticsService.check_role(message.from_user, 'Manager'))
async def assign_task_command(message: types.Message):
    user = message.from_user
    task_id = int(message.text.split()[1])
    worker_id = int(message.text.split()[2])

    if not task_id or not worker_id:
        await message.answer('Invalid task assignment. Please enter the task ID and worker ID in the following format: assign_task <task_id> <worker_id>')
        return

    task = TasksService.get_task_by_id(task_id)

    if not task or task.status == 'completed':
        await message.answer('Invalid task assignment. The task with the given ID does not exist or has already been completed')
        return

    TasksService.assign_task(task, worker_id)
    await message.answer(f'Task "{task.title}" has been assigned to worker {task.worker.username}')

@dp.message_handler(lambda message: message.text.startswith('log_expense') and StatisticsService.check_role(message.from_user, 'Manager'))
async def log_expense_command(message: types.Message):
    user = message.from_user
    amount = float(message.text.split()[1])
    currency = message.text.split()[2]

    if not amount or not currency or (currency != 'USD' and currency != 'RUB'):
        await message.answer('Invalid expense logging. Please enter the amount and currency in the following format: log_expense <amount> <currency (USD or RUB)>')
        return

    ExpensesService.log_expense(user.id, amount, currency)
    await message.answer(f'Expense of {amount} {currency} has been logged')

@dp.message_handler(lambda message: message.text.startswith('statistics') and StatisticsService.check_role(message.from_user, 'Manager'))
async def statistics_command(message: types.Message):
    user = message.from_user
    on_time, missed = StatisticsService.get_worker_statistics(user.id)
    total_usd, total_rub, _ = ExpensesService.get_total_expenses(user.channel_id)
    total_payments = PaymentService.get_total_payments(user.channel_id)

    await message.answer(
        f'You have completed {on_time} tasks on time and missed {missed} deadlines.\n'
        f'Total expenses: {total_usd} USD, {total_rub} RUB.\n'
        f'Total payments: {total_payments} USD.'
    )
