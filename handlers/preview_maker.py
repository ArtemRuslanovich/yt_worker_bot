import datetime
from aiogram import Dispatcher, Router, types
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from database.models import Task
from database.repository import DatabaseRepository
from database import SessionLocal
from keyboards.preview_maker_buttons import get_preview_maker_buttons
from middlewares.authentication import Authenticator
from services.tasks import TasksService
from enum import Enum

class TaskStatus(Enum):
    AWAITING = "в ожидании выполнения"
    IN_PROGRESS = "в процессе выполнения"
    UNDER_REVIEW = "на проверке"
    COMPLETED = "выполнено"

router = Router()

class PreviewTaskAction(StatesGroup):
    accept_task_id = State()
    submit_task_id = State()

async def preview_maker_role_required(message: types.Message, state: FSMContext, db_repository):
    user_data = await state.get_data()
    username = user_data.get('username')
    role = user_data.get('role')
    authenticator = Authenticator(db_repository)

    user = db_repository.get_user_by_username(username)
    if not user or not authenticator.check_role(user, 'PreviewMaker'):
        await message.answer("Access denied: you do not have preview maker rights.")
        return False
    return True

@router.message(Command(commands='preview_maker_menu'))
async def preview_maker_menu_command(message: types.Message, state: FSMContext):
    with SessionLocal() as db_session:
        db_repository = DatabaseRepository(db_session)
        if not await preview_maker_role_required(message, state, db_repository):
            return
        await message.answer("Выберите действие:", reply_markup=get_preview_maker_buttons())

@router.callback_query(lambda c: c.data in ['pm_accept_task', 'pm_submit_task', 'pm_view_tasks'])
async def process_callback_preview_maker(callback_query: types.CallbackQuery, state: FSMContext):
    action = callback_query.data
    await callback_query.answer()

    if action == 'pm_accept_task':
        await callback_query.message.answer("Введите ID задачи для принятия:")
        await state.set_state(PreviewTaskAction.accept_task_id)
    elif action == 'pm_submit_task':
        await callback_query.message.answer("Введите ID задачи для сдачи:")
        await state.set_state(PreviewTaskAction.submit_task_id)
    elif action == 'pm_view_tasks':
        await view_tasks(callback_query.message, state)

@router.message(PreviewTaskAction.accept_task_id)
async def process_accept_task_id(message: types.Message, state: FSMContext):
    task_id = message.text

    with SessionLocal() as db_session:
        db_repository = DatabaseRepository(db_session)
        task = db_repository.get_item_by_id(Task, task_id)

        if not task or task.status != TaskStatus.AWAITING.value:
            await message.answer('Задача не найдена или не может быть принята.')
            return

        task.status = TaskStatus.IN_PROGRESS.value
        db_session.commit()

        await message.answer(f'Задача с ID {task_id} принята в работу.')
        await state.clear()

@router.message(PreviewTaskAction.submit_task_id)
async def process_submit_task_id(message: types.Message, state: FSMContext):
    task_id = message.text

    with SessionLocal() as db_session:
        db_repository = DatabaseRepository(db_session)
        task = db_repository.get_item_by_id(Task, task_id)

        if not task or task.status != TaskStatus.IN_PROGRESS.value:
            await message.answer('Задача не найдена или не может быть сдана.')
            return

        task.status = TaskStatus.UNDER_REVIEW.value
        task.actual_completion_date = datetime.datetime.now()
        db_session.commit()

        await message.answer(f'Задача с ID {task_id} сдана на проверку.')
        await state.clear()

@router.message(Command(commands='pm_view_tasks'))
async def view_tasks(message: types.Message, state: FSMContext):
    with SessionLocal() as db_session:
        db_repository = DatabaseRepository(db_session)
        if not await preview_maker_role_required(message, state, db_repository):
            return

        user_data = await state.get_data()
        username = user_data.get('username')
        preview_maker = db_repository.get_user_by_username(username)

        if not preview_maker:
            await message.answer('Работник не найден.')
            return

        tasks_service = TasksService(db_repository)
        tasks = tasks_service.get_tasks_by_user_id(preview_maker.id)

        response = "Ваши задачи:\n\n"
        response += "\n".join([f"ID: {task.id}, Title: {task.title}, Status: {task.status}" for task in tasks])

        await message.answer(response)

def register_handlers(dp: Dispatcher):
    dp.include_router(router)
