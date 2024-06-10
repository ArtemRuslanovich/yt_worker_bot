from asyncio import Task
import datetime
import shlex
import logging
from aiogram import Dispatcher, Router, types
from aiogram.filters.command import Command
from database.repository import DatabaseRepository
from middlewares.authentication import Authenticator
from services.tasks import TasksService
from database import SessionLocal
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

router = Router()

class TaskCreation(StatesGroup):
    waiting_for_title = State()
    waiting_for_description = State()
    waiting_for_theme = State()
    waiting_for_worker_username = State()
    waiting_for_deadline = State()
    waiting_for_channel_name = State()

async def manager_role_required(message: types.Message, state: FSMContext, db_repository):
    user_data = await state.get_data()
    logging.info(f"State user data: {user_data}")
    username = user_data.get('username')
    role = user_data.get('role')
    authenticator = Authenticator(db_repository)

    user = db_repository.get_user_by_username(username)

    logging.info(f"Checking role for user: {user}")
    if not user or not authenticator.check_role(user, 'Manager'):
        await message.answer("Access denied: you do not have manager rights.")
        return False
    return True

@router.message(Command(commands='create_task'))
async def create_task_command(message: types.Message, state: FSMContext):
    with SessionLocal() as db_session:
        db_repository = DatabaseRepository(db_session)
        if not await manager_role_required(message, state, db_repository):
            return

        await message.answer("Введите название задачи:")
        await state.set_state(TaskCreation.waiting_for_title)

@router.message(TaskCreation.waiting_for_title)
async def process_title(message: types.Message, state: FSMContext):
    await state.update_data(title=message.text)
    await message.answer("Введите описание задачи:")
    await state.set_state(TaskCreation.waiting_for_description)

@router.message(TaskCreation.waiting_for_description)
async def process_description(message: types.Message, state: FSMContext):
    await state.update_data(description=message.text)
    await message.answer("Введите тему задачи:")
    await state.set_state(TaskCreation.waiting_for_theme)

@router.message(TaskCreation.waiting_for_theme)
async def process_theme(message: types.Message, state: FSMContext):
    await state.update_data(theme=message.text)
    await message.answer("Введите имя пользователя, которому назначается задача:")
    await state.set_state(TaskCreation.waiting_for_worker_username)

@router.message(TaskCreation.waiting_for_worker_username)
async def process_worker_username(message: types.Message, state: FSMContext):
    await state.update_data(worker_username=message.text)
    await message.answer("Введите дедлайн задачи (формат: YYYY-MM-DD):")
    await state.set_state(TaskCreation.waiting_for_deadline)

@router.message(TaskCreation.waiting_for_deadline)
async def process_deadline(message: types.Message, state: FSMContext):
    try:
        deadline = datetime.datetime.strptime(message.text, '%Y-%m-%d')
        await state.update_data(deadline=deadline)
        await message.answer("Введите название канала:")
        await state.set_state(TaskCreation.waiting_for_channel_name)
    except ValueError:
        await message.answer('Неправильный формат даты. Пожалуйста, используйте формат YYYY-MM-DD.')

@router.message(TaskCreation.waiting_for_channel_name)
async def process_channel_name(message: types.Message, state: FSMContext):
    data = await state.get_data()
    channel_name = message.text
    worker_username = data['worker_username']
    
    with SessionLocal() as db_session:
        db_repository = DatabaseRepository(db_session)
        worker = db_repository.get_user_by_username(worker_username)
        channel = db_repository.get_channel_by_name(channel_name)
        
        if not worker or not channel:
            await message.answer('Пользователь или канал не найдены.')
            return
        
        task_service = TasksService(db_repository)
        task = task_service.create_task(
            worker_id=worker.id,
            title=data['title'],
            description=data['description'],
            theme=data['theme'],
            deadline=data['deadline'],
            status="pending",
            channel_id=channel.id
        )
        
        await message.answer(f'Задача "{task.title}" с темой "{task.theme}" создана и назначена пользователю {worker.username} в канале {channel.name}.')
        await state.clear()

class TaskChecking(StatesGroup):
    waiting_for_task_id = State()
    waiting_for_new_status = State()

@router.message(Command(commands='check_task'))
async def check_task_command(message: types.Message, state: FSMContext):
    with SessionLocal() as db_session:
        db_repository = DatabaseRepository(db_session)
        if not await manager_role_required(message, state, db_repository):
            return

        await message.answer("Введите ID задачи:")
        await state.set_state(TaskChecking.waiting_for_task_id)

@router.message(TaskChecking.waiting_for_task_id)
async def process_task_id(message: types.Message, state: FSMContext):
    await state.update_data(task_id=message.text)
    await message.answer("Введите новый статус задачи:")
    await state.set_state(TaskChecking.waiting_for_new_status)

@router.message(TaskChecking.waiting_for_new_status)
async def process_new_status(message: types.Message, state: FSMContext):
    new_status = message.text
    data = await state.get_data()
    task_id = data['task_id']

    with SessionLocal() as db_session:
        db_repository = DatabaseRepository(db_session)
        task = db_repository.get_item_by_id(Task, task_id)
        
        if not task:
            await message.answer('Задача не найдена.')
            return
        
        task.status = new_status
        db_session.commit()
        
        await message.answer(f'Статус задачи с ID {task_id} обновлен на "{new_status}".')
        await state.clear()


@router.message(Command(commands='view_task'))
async def view_task_command(message: types.Message, state: FSMContext):
    with SessionLocal() as db_session:
        db_repository = DatabaseRepository(db_session)
        if not await manager_role_required(message, state, db_repository):
            return

        tasks_service = TasksService(db_repository)
        pending_tasks = tasks_service.get_tasks_by_status('pending')
        in_progress_tasks = tasks_service.get_tasks_by_status('in_progress')
        completed_tasks = tasks_service.get_tasks_by_status('completed')

        response = "Задачи:\n\n"
        response += "В ожидании выполнения:\n"
        response += "\n".join([f"ID: {task.id}, Title: {task.title}" for task in pending_tasks]) + "\n\n"
        
        response += "В процессе выполнения:\n"
        response += "\n".join([f"ID: {task.id}, Title: {task.title}" for task in in_progress_tasks]) + "\n\n"
        
        response += "Выполненные:\n"
        response += "\n".join([f"ID: {task.id}, Title: {task.title}" for task in completed_tasks])

        await message.answer(response)

class SalarySetting(StatesGroup):
    waiting_for_worker_username = State()
    waiting_for_amount = State()

@router.message(Command(commands='set_salary'))
async def set_salary_command(message: types.Message, state: FSMContext):
    with SessionLocal() as db_session:
        db_repository = DatabaseRepository(db_session)
        if not await manager_role_required(message, state, db_repository):
            return

        await message.answer("Введите имя пользователя работника:")
        await state.set_state(SalarySetting.waiting_for_worker_username)

@router.message(SalarySetting.waiting_for_worker_username)
async def process_worker_username_salary(message: types.Message, state: FSMContext):
    await state.update_data(worker_username=message.text)
    await message.answer("Введите сумму зарплаты:")
    await SalarySetting.waiting_for_amount.set()

@router.message(SalarySetting.waiting_for_amount)
async def process_salary_amount(message: types.Message, state: FSMContext):
    try:
        amount = float(message.text)
        data = await state.get_data()
        worker_username = data['worker_username']

        with SessionLocal() as db_session:
            db_repository = DatabaseRepository(db_session)
            worker = db_repository.get_user_by_username(worker_username)
            
            if not worker:
                await message.answer('Работник не найден.')
                return
            
            worker.salary = amount
            db_session.commit()
            
            await message.answer(f'Зарплата работника {worker.username} установлена на {amount}.')
            await state.clear()
    except ValueError:
        await message.answer('Пожалуйста, введите корректное числовое значение для суммы.')

def register_handlers(dp: Dispatcher):
    dp.include_router(router)