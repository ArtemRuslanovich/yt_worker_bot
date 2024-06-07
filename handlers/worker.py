import datetime
from aiogram import Router, types
from aiogram.filters import Command
from aiogram.types import Message

from services.statistics import StatisticsService
from services.tasks import TasksService

router = Router()

@router.message(Command(commands='submit_task'))
async def submit_task_command(message: Message):
    if not StatisticsService.check_role(message.from_user, 'Worker'):
        return
    user = message.from_user
    text = message.text.split()
    task_id = int(text[1]) if len(text) > 1 else None
    link = text[2] if len(text) > 2 else None

    if not task_id or not link:
        await message.answer('Invalid task submission. Please enter the task ID and link in the following format: submit_task <task_id> <link>')
        return

    task = TasksService.get_task_by_id(task_id)

    if not task or task.worker_id != user.id or task.status == 'completed':
        await message.answer('Invalid task submission. You do not have a task with the given ID or the task has already been completed')
        return

    TasksService.update_task(task_id, 'completed', datetime.datetime.now())
    await message.answer(f'Task "{task.title}" has been submitted and is pending review')

@router.message(Command(commands='view_tasks'))
async def view_tasks_command(message: Message):
    if not StatisticsService.check_role(message.from_user, 'Worker'):
        return
    user = message.from_user
    tasks = TasksService.get_tasks_by_worker_id(user.id)

    if not tasks:
        await message.answer('You do not have any tasks assigned to you')
        return

    task_messages = [f'{i+1}. {task.title} (Deadline: {task.deadline.strftime("%Y-%m-%d")})' for i, task in enumerate(tasks)]
    await message.answer('\n'.join(task_messages))

@router.message(Command(commands='statistics'))
async def statistics_command(message: Message):
    if not StatisticsService.check_role(message.from_user, 'Worker'):
        return
    user = message.from_user
    on_time, missed = StatisticsService.get_worker_statistics(user.id)
    total_payment = TasksService.get_worker_payment(user.id)

    await message.answer(
        f'You have completed {on_time} tasks on time and missed {missed} deadlines.\n'
        f'Your total payment for completed tasks is {total_payment} USD.'
    )
