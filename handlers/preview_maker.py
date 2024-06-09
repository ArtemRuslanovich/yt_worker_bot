import datetime
from aiogram import Dispatcher, Router
from aiogram.types import Message
from aiogram.filters.command import Command
from database.repository import DatabaseRepository
from middlewares.authentication import Authenticator
from services.preview import PreviewsService
from services.statistics import StatisticsService
from database import SessionLocal
from aiogram.fsm.context import FSMContext
import logging

router = Router()

async def preview_maker_role_required(message: Message, state: FSMContext, db_repository):
    user_data = await state.get_data()
    logging.info(f"State user data: {user_data}")  # Отладочное сообщение
    username = user_data.get('username')
    role = user_data.get('role')
    authenticator = Authenticator(db_repository)

    user = db_repository.get_user_by_username(username)

    logging.info(f"Checking role for user: {user}")  # Отладочное сообщение
    if not user or not authenticator.check_role(user, 'PreviewMaker'):
        await message.answer("Access denied: you do not have preview maker rights.")
        return False
    return True

@router.message(Command(commands='submit_preview'))
async def submit_preview_command(message: Message, state: FSMContext):
    with SessionLocal() as db_session:
        db_repository = DatabaseRepository(db_session)
        if not await preview_maker_role_required(message, state, db_repository):
            return

        text = message.text.split()
        preview_id = int(text[1]) if len(text) > 1 else None
        link = text[2] if len(text) > 2 else None

        if not preview_id or not link:
            await message.answer('Invalid preview submission. Please enter the preview ID and link correctly.')
            return

        preview = PreviewsService(db_repository).get_preview_by_id(preview_id)

        if not preview or preview.preview_maker_id != message.from_user.id or preview.status == 'completed':
            await message.answer('Invalid preview submission. Preview either does not exist, is completed, or does not belong to you.')
            return

        PreviewsService(db_repository).update_preview(preview_id, 'completed', link)
        await message.answer(f'Preview for video "{preview.video.title}" has been submitted and is pending review.')

@router.message(Command(commands='view_previews'))
async def view_previews_command(message: Message, state: FSMContext):
    with SessionLocal() as db_session:
        db_repository = DatabaseRepository(db_session)
        if not await preview_maker_role_required(message, state, db_repository):
            return

        previews = PreviewsService(db_repository).get_previews_by_preview_maker_id(message.from_user.id)

        if not previews:
            await message.answer('You do not have any previews assigned to you.')
            return

        preview_messages = [f'{i+1}. {preview.video.title} (Deadline: {preview.deadline.strftime("%Y-%m-%d")})' for i, preview in enumerate(previews)]
        await message.answer('\n'.join(preview_messages))

@router.message(Command(commands='statistics'))
async def statistics_command(message: Message, state: FSMContext):
    with SessionLocal() as db_session:
        db_repository = DatabaseRepository(db_session)
        if not await preview_maker_role_required(message, state, db_repository):
            return

        total_previews = PreviewsService(db_repository).get_preview_maker_statistics(message.from_user.id)
        total_payment = PreviewsService(db_repository).get_preview_maker_payment(message.from_user.id)

        await message.answer(
            f'You have completed {total_previews} previews.\n'
            f'Your total payment for completed previews is {total_payment} USD.'
        )

@router.message(Command(commands='get_technical_specification'))
async def get_technical_specification_command(message: Message, state: FSMContext):
    with SessionLocal() as db_session:
        db_repository = DatabaseRepository(db_session)
        if not await preview_maker_role_required(message, state, db_repository):
            return

        args = message.text.split()
        if len(args) != 2:
            await message.answer("Usage: /get_technical_specification <preview_id>")
            return

        preview_id = int(args[1])
        technical_specification = PreviewsService(db_repository).get_technical_specification(preview_id)

        if not technical_specification:
            await message.answer("Technical specification not found or you do not have access to it.")
            return

        await message.answer(f"Technical Specification for Preview ID {preview_id}: {technical_specification}")

@router.message(Command(commands='set_preview_payment'))
async def set_preview_payment_command(message: Message, state: FSMContext):
    with SessionLocal() as db_session:
        db_repository = DatabaseRepository(db_session)
        if not await preview_maker_role_required(message, state, db_repository):
            return

        args = message.text.split()
        if len(args) != 3:
            await message.answer("Usage: /set_preview_payment <preview_id> <amount>")
            return

        preview_id, amount = int(args[1]), float(args[2])
        result = PreviewsService(db_repository).set_preview_payment(preview_id, amount)

        if result:
            await message.answer(f"Payment for preview ID {preview_id} set to ${amount}.")
        else:
            await message.answer("Failed to set payment. Check preview ID and your permissions.")

def register_handlers(dp: Dispatcher):
    dp.include_router(router)
