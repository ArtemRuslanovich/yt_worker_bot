import datetime
import logging
from aiogram import Router, types
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from database.models import Task
from database.repository import DatabaseRepository
from database import SessionLocal
from middlewares.authentication import Authenticator
from services.tasks import TasksService

router = Router()

class TaskAction(StatesGroup):
    waiting_for_task_id = State()

async def worker_role_required(message: types.Message, state: FSMContext, db_repository):
    user_data = await state.get_data()
    logging.info(f"State user data: {user_data}")
    username = user_data.get('username')
    role = user_data.get('role')
    authenticator = Authenticator(db_repository)

    user = db_repository.get_user_by_username(username)

    logging.info(f"Checking role for user: {user}")
    if not user or not authenticator.check_role(user, 'Worker'):
        await message.answer("Access denied: you do not have worker rights.")
        return False
    return True

@router.message(Command(commands='accept_task'))
async def accept_task_command(message: types.Message, state: FSMContext):
    with SessionLocal() as db_session:
        db_repository = DatabaseRepository(db_session)
        if not await worker_role_required(message, state, db_repository):
            return

        await message.answer("Введите ID задачи для принятия:")
        await state.set_state(TaskAction.waiting_for_task_id)

@router.message(TaskAction.waiting_for_task_id)
async def process_accept_task_id(message: types.Message, state: FSMContext):
    task_id = message.text

    with SessionLocal() as db_session:
        db_repository = DatabaseRepository(db_session)
        task = db_repository.get_item_by_id(Task, task_id)

        if not task or task.status != "pending":
            await message.answer('Задача не найдена или не может быть принята.')
            return

        task.status = "in_progress"
        db_session.commit()

        await message.answer(f'Задача с ID {task_id} принята в работу.')
        await state.clear()

@router.message(Command(commands='submit_task'))
async def submit_task_command(message: types.Message, state: FSMContext):
    with SessionLocal() as db_session:
        db_repository = DatabaseRepository(db_session)
        if not await worker_role_required(message, state, db_repository):
            return

        await message.answer("Введите ID задачи для сдачи:")
        await state.set_state(TaskAction.waiting_for_task_id)

@router.message(TaskAction.waiting_for_task_id)
async def process_submit_task_id(message: types.Message, state: FSMContext):
    task_id = message.text

    with SessionLocal() as db_session:
        db_repository = DatabaseRepository(db_session)
        task = db_repository.get_item_by_id(Task, task_id)

        if not task or task.status != "in_progress":
            await message.answer('Задача не найдена или не может быть сдана.')
            return

        task.status = "submitted"
        task.actual_completion_date = datetime.datetime.now()
        db_session.commit()

        await message.answer(f'Задача с ID {task_id} сдана на проверку.')
        await state.clear()

@router.message(Command(commands='view_tasks'))
async def view_tasks_command(message: types.Message, state: FSMContext):
    with SessionLocal() as db_session:
        db_repository = DatabaseRepository(db_session)
        if not await worker_role_required(message, state, db_repository):
            return

        user_data = await state.get_data()
        username = user_data.get('username')
        worker = db_repository.get_user_by_username(username)

        if not worker:
            await message.answer('Работник не найден.')
            return

        tasks_service = TasksService(db_repository)
        tasks = tasks_service.get_tasks_by_user_id(worker.id)

        response = "Ваши задачи:\n\n"
        response += "\n".join([f"ID: {task.id}, Title: {task.title}, Status: {task.status}" for task in tasks])

        await message.answer(response)
