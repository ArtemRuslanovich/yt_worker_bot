# handlers/worker.py
import datetime
from aiogram import Router, Command, Message
from database.repository import DatabaseRepository
from services.statistics import StatisticsService
from services.tasks import TasksService
from database import SessionLocal

router = Router()

@router.message(Command(commands='submit_task'))
async def submit_task_command(message: Message):
    # Создание сессии базы данных
    db_session = SessionLocal()
    db_repository = DatabaseRepository(db_session)

    if not StatisticsService(db_repository).check_role(message.from_user.id, 'Worker'):
        db_session.close()
        return

    user = message.from_user
    text = message.text.split()
    task_id = int(text[1]) if len(text) > 1 else None
    link = text[2] if len(text) > 2 else None

    if not task_id or not link:
        await message.answer('Invalid task submission. Please enter the task ID and link in the following format: submit_task <task_id> <link>')
        db_session.close()
        return

    task = TasksService(db_repository).get_task_by_id(task_id)

    if not task or task.worker_id != user.id or task.status == 'completed':
        await message.answer('Invalid task submission. You do not have a task with the given ID or the task has already been completed')
        db_session.close()
        return

    TasksService(db_repository).update_task(task_id, 'completed', datetime.datetime.now())
    await message.answer(f'Task "{task.title}" has been submitted and is pending review')
    db_session.close()

@router.message(Command(commands='view_tasks'))
async def view_tasks_command(message: Message):
    # Создание сессии базы данных
    db_session = SessionLocal()
    db_repository = DatabaseRepository(db_session)

    if not StatisticsService(db_repository).check_role(message.from_user.id, 'Worker'):
        db_session.close()
        return

    user = message.from_user
    tasks = TasksService(db_repository).get_tasks_by_worker_id(user.id)

    if not tasks:
        await message.answer('You do not have any tasks assigned to you')
        db_session.close()
        return

    task_messages = [f'{i+1}. {task.title} (Deadline: {task.deadline.strftime("%Y-%m-%d")})' for i, task in enumerate(tasks)]
    await message.answer('\n'.join(task_messages))
    db_session.close()

@router.message(Command(commands='statistics'))
async def statistics_command(message: Message):
    # Создание сессии базы данных
    db_session = SessionLocal()
    db_repository = DatabaseRepository(db_session)

    if not StatisticsService(db_repository).check_role(message.from_user.id, 'Worker'):
        db_session.close()
        return

    user = message.from_user
    on_time, missed = StatisticsService(db_repository).get_worker_statistics(user.id)
    total_payment = TasksService(db_repository).get_worker_payment(user.id)

    await message.answer(
        f'You have completed {on_time} tasks on time and missed {missed} deadlines.\n'
        f'Your total payment for completed tasks is {total_payment} USD.'
    )
    db_session.close()
