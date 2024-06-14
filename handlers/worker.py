from enum import Enum
from aiogram import Dispatcher, Router, types
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from database.models import Task
from database.repository import DatabaseRepository
from database import SessionLocal
from keyboards.worker_buttons import get_worker_buttons
from middlewares.authentication import Authenticator
from services.tasks import TasksService

router = Router()

class TaskStatus(Enum):
    AWAITING = "в ожидании выполнения"
    IN_PROGRESS = "в процессе выполнения"
    UNDER_REVIEW = "на проверке"
    COMPLETED = "выполнено"

class TaskAction(StatesGroup):
    accept_task_id = State()
    submit_task_id = State()

async def worker_role_required(message: types.Message, state: FSMContext, db_repository):
    user_data = await state.get_data()
    username = user_data.get('username')
    role = user_data.get('role')
    authenticator = Authenticator(db_repository)

    user = db_repository.get_user_by_username(username)
    if not user or not authenticator.check_role(user, 'Worker'):
        await message.answer("Access denied: you do not have worker rights.")
        return False
    return True

@router.message(Command(commands='worker_menu'))
async def worker_menu_command(message: types.Message, state: FSMContext):
    with SessionLocal() as db_session:
        db_repository = DatabaseRepository(db_session)
        if not await worker_role_required(message, state, db_repository):
            return
        await message.answer("Выберите действие:", reply_markup=get_worker_buttons())

@router.callback_query(lambda c: c.data in ['accept_task', 'submit_task', 'view_tasks'])
async def process_callback_worker(callback_query: types.CallbackQuery, state: FSMContext):
    action = callback_query.data
    await callback_query.answer()

    if action == 'accept_task':
        await callback_query.message.answer("Введите ID задачи для принятия:")
        await state.set_state(TaskAction.accept_task_id)
    elif action == 'submit_task':
        await callback_query.message.answer("Введите ID задачи для сдачи:")
        await state.set_state(TaskAction.submit_task_id)
    elif action == 'view_tasks':
        await view_tasks(callback_query.message, state)

@router.message(TaskAction.accept_task_id)
async def process_accept_task_id(message: types.Message, state: FSMContext):
    task_id = message.text
    with SessionLocal() as db_session:
        db_repository = DatabaseRepository(db_session)
        task = db_repository.get_item_by_id(Task, task_id)
        if task and task.status == TaskStatus.AWAITING.value:
            task.status = TaskStatus.IN_PROGRESS.value
            db_session.commit()
            await message.answer(f'Задача с ID {task_id} принята в работу.')
        else:
            await message.answer('Задача не найдена или уже в работе.')
        await state.clear()

@router.message(TaskAction.submit_task_id)
async def process_submit_task_id(message: types.Message, state: FSMContext):
    task_id = message.text
    with SessionLocal() as db_session:
        db_repository = DatabaseRepository(db_session)
        task = db_repository.get_item_by_id(Task, task_id)
        if task and task.status == TaskStatus.IN_PROGRESS.value:
            task.status = TaskStatus.UNDER_REVIEW.value
            db_session.commit()
            await message.answer(f'Задача с ID {task_id} сдана на проверку.')
        else:
            await message.answer('Задача не найдена или не в процессе выполнения.')
        await state.clear()

@router.message(Command(commands='view_tasks'))
async def view_tasks(message: types.Message, state: FSMContext):
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

def register_handlers(dp: Dispatcher):
    dp.include_router(router)