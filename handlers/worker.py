import datetime
from aiogram import Dispatcher, Router
from aiogram.types import Message
from aiogram.filters.command import Command
from database.repository import DatabaseRepository
from services.tasks import TasksService
from services.statistics import StatisticsService
from database import SessionLocal

router = Router()

async def worker_role_required(message: Message, db_repository):
    """Проверка, что пользователь имеет роль 'Worker'."""
    if not StatisticsService(db_repository).check_role(message.from_user.id, 'Worker'):
        await message.answer("Доступ запрещен: у вас нет прав работника.")
        return False
    return True

@router.message(Command(commands='submit_task'))
async def submit_task_command(message: Message):
    with SessionLocal() as db_session:
        db_repository = DatabaseRepository(db_session)
        if not await worker_role_required(message, db_repository):
            return

        text = message.text.split()
        task_id = int(text[1]) if len(text) > 1 else None
        link = text[2] if len(text) > 2 else None

        if not task_id or not link:
            await message.answer('Invalid task submission. Please enter the task ID and link correctly.')
            return

        task = TasksService(db_repository).get_task_by_id(task_id)

        if not task or task.user_id != message.from_user.id or task.status == 'completed':
            await message.answer('Invalid task submission. Task either does not exist, is completed, or does not belong to you.')
            return

        TasksService(db_repository).update_task(task_id, status='completed', link=link, actual_completion_date=datetime.datetime.now())
        await message.answer(f'Task "{task.title}" has been submitted and is pending review.')

@router.message(Command(commands='view_tasks'))
async def view_tasks_command(message: Message):
    with SessionLocal() as db_session:
        db_repository = DatabaseRepository(db_session)
        if not await worker_role_required(message, db_repository):
            return

        tasks = TasksService(db_repository).get_tasks_by_worker_id(message.from_user.id)

        if not tasks:
            await message.answer('You do not have any tasks assigned to you.')
            return

        task_messages = [f'{i+1}. {task.title} (Deadline: {task.deadline.strftime("%Y-%m-%d")})' for i, task in enumerate(tasks)]
        await message.answer('\n'.join(task_messages))

@router.message(Command(commands='statistics'))
async def statistics_command(message: Message):
    with SessionLocal() as db_session:
        db_repository = DatabaseRepository(db_session)
        if not await worker_role_required(message, db_repository):
            return

        stats = StatisticsService(db_repository).get_worker_statistics(message.from_user.id)
        total_payment = TasksService(db_repository).get_worker_payment(message.from_user.id)

        await message.answer(
            f'You have completed {stats["on_time"]} tasks on time and missed {stats["missed"]} deadlines.\n'
            f'Your total payment for completed tasks is {total_payment} USD.'
        )

def register_handlers(dp: Dispatcher):
    dp.include_router(router)