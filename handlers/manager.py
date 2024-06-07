from aiogram import Router, types
from aiogram.filters import Command
from aiogram.types import Message
from services.expenses import ExpensesService
from services.payment import PaymentService
import datetime

from services.statistics import StatisticsService
from services.tasks import TasksService

router = Router()


@router.message(Command(commands='create_task'))
async def create_task_command(message: Message):
    if not StatisticsService.check_role(message.from_user, 'Manager'):
        return
    user = message.from_user
    text = message.text.split()
    title = text[1] if len(text) > 1 else None
    description = text[2] if len(text) > 2 else None
    thumbnail_draft = text[3] if len(text) > 3 else None
    worker_id = int(text[4]) if len(text) > 4 else None
    deadline = datetime.datetime.strptime(text[5], '%Y-%m-%d') if len(text) > 5 else None

    if not title or not worker_id or not deadline:
        await message.answer('Некорректное создание задачи. Пожалуйста, введите информацию о задаче в следующем формате: create_task <название> <описание> <эскиз_задачи> <идентификатор работника_ид> <срок выполнения>')
        return

    task = TasksService.create_task(title, description, thumbnail_draft, worker_id, deadline, deadline)
    await message.answer(f'Задание "{task.title}" было создано и возложено на плечи {task.worker.username}')

@router.message(Command(commands='assign_task'))
async def assign_task_command(message: Message):
    if not StatisticsService.check_role(message.from_user, 'Manager'):
        return
    user = message.from_user
    text = message.text.split()
    task_id = int(text[1]) if len(text) > 1 else None
    worker_id = int(text[2]) if len(text) > 2 else None

    if not task_id or not worker_id:
        await message.answer('Неверное назначение задачи. Пожалуйста, введите идентификатор задачи и идентификатор работника в следующем формате: assign_task <идентификатор_задачи> <идентификатор_работника>')
        return

    task = TasksService.get_task_by_id(task_id)

    if not task or task.status == 'completed':
        await message.answer('Неверное назначение задачи. Задача с указанным идентификатором не существует или уже выполнена')
        return

    TasksService.assign_task(task, worker_id)
    await message.answer(f'Задание "{task.title}" возложено на плечи {task.worker.username}')

@router.message(Command(commands='log_expense'))
async def log_expense_command(message: Message):
    if not StatisticsService.check_role(message.from_user, 'Manager'):
        return
    user = message.from_user
    text = message.text.split()
    amount = float(text[1]) if len(text) > 1 else None
    currency = text[2] if len(text) > 2 else None

    if not amount or not currency or (currency != 'USD' and currency != 'RUB'):
        await message.answer('Неверный журнал учета расходов. Пожалуйста, введите сумму и валюту в следующем формате: log_expense <сумма> <валюта (USD или RUB)>')
        return

    ExpensesService.log_expense(user.id, amount, currency)
    await message.answer(f'Expense of {amount} {currency} has been logged')

@router.message(Command(commands='statistics'))
async def statistics_command(message: Message):
    if not StatisticsService.check_role(message.from_user, 'Manager'):
        return
    user = message.from_user
    on_time, missed = StatisticsService.get_worker_statistics(user.id)
    total_usd, total_rub, _ = ExpensesService.get_total_expenses(user.channel_id)
    total_payments = PaymentService.get_total_payments(user.channel_id)

    await message.answer(
        f'You have completed {on_time} tasks on time and missed {missed} deadlines.\n'
        f'Total expenses: {total_usd} USD, {total_rub} RUB.\n'
        f'Total payments: {total_payments} USD.'
    )