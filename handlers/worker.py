import datetime
import asyncio
from aiogram import Bot, Dispatcher, Router
from aiogram.types import Message
from aiogram.filters.command import Command
from database.repository import DatabaseRepository
from middlewares.authentication import Authenticator
from services.tasks import TasksService
from services.statistics import StatisticsService
from database import SessionLocal
from aiogram.fsm.context import FSMContext
import logging

router = Router()

async def worker_role_required(message: Message, state: FSMContext, db_repository):
    user_data = await state.get_data()
    logging.info(f"State user data: {user_data}")  # Отладочное сообщение
    username = user_data.get('username')
    role = user_data.get('role')
    authenticator = Authenticator(db_repository)

    user = db_repository.get_user_by_username(username)

    logging.info(f"Checking role for user: {user}")  # Отладочное сообщение
    if not user or not authenticator.check_role(user, 'Worker'):
        await message.answer("Access denied: you do not have worker rights.")
        return False
    return True

@router.message(Command(commands='submit_task'))
async def submit_task_command(message: Message, state: FSMContext):
    with SessionLocal() as db_session:
        db_repository = DatabaseRepository(db_session)
        if not await worker_role_required(message, state, db_repository):
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
async def view_tasks_command(message: Message, state: FSMContext):
    with SessionLocal() as db_session:
        db_repository = DatabaseRepository(db_session)
        if not await worker_role_required(message, state, db_repository):
            return

        tasks = TasksService(db_repository).get_tasks_by_worker_id(message.from_user.id)

        if not tasks:
            await message.answer('You do not have any tasks assigned to you.')
            return

        task_messages = [f'{i+1}. {task.title} (Deadline: {task.deadline.strftime("%Y-%m-%d")})' for i, task in enumerate(tasks)]
        await message.answer('\n'.join(task_messages))

@router.message(Command(commands='statistics'))
async def statistics_command(message: Message, state: FSMContext):
    with SessionLocal() as db_session:
        db_repository = DatabaseRepository(db_session)
        if not await worker_role_required(message, state, db_repository):
            return

        stats = StatisticsService(db_repository).get_worker_statistics(message.from_user.id)
        total_payment = TasksService(db_repository).get_worker_payment(message.from_user.id)

        await message.answer(
            f'You have completed {stats["on_time"]} tasks on time and missed {stats["missed"]} deadlines.\n'
            f'Your total payment for completed tasks is {total_payment} USD.'
        )

async def send_daily_topics(bot: Bot):
    while True:
        with SessionLocal() as db_session:
            db_repository = DatabaseRepository(db_session)
            topics = db_repository.get_daily_topics()  # Этот метод должен быть реализован в репозитории
            for worker in db_repository.get_all_workers():
                await bot.send_message(worker.telegram_id, "\n".join(topics))
        await asyncio.sleep(86400)  # Пауза на 24 часа

def setup_daily_topics(dp: Dispatcher):
    dp.loop.create_task(send_daily_topics())

async def send_deadline_reminders(bot: Bot):
    while True:
        with SessionLocal() as db_session:
            db_repository = DatabaseRepository(db_session)
            overdue_tasks = db_repository.get_overdue_tasks()
            for task in overdue_tasks:
                user = db_repository.get_user_by_id(task.user_id)
                await bot.send_message(user.telegram_id, f'You missed the deadline for task "{task.title}". Please submit it as soon as possible.')
        await asyncio.sleep(3600)  # Пауза на 1 час

def setup_overdue_notifications(dp: Dispatcher):
    dp.loop.create_task(send_deadline_reminders())

def register_handlers(dp: Dispatcher):
    dp.include_router(router)
    setup_daily_topics(dp)
    setup_overdue_notifications(dp)