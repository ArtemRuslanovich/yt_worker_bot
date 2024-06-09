from aiogram import Dispatcher, Router
from aiogram.types import Message
from aiogram.filters.command import Command
from database.repository import DatabaseRepository
from services.preview import PreviewsService
from services.statistics import StatisticsService
from database import SessionLocal

router = Router()

async def preview_maker_role_required(message: Message, db_repository):
    """Проверка, что пользователь имеет роль 'PreviewMaker'."""
    if not StatisticsService(db_repository).check_role(message.from_user.id, 'PreviewMaker'):
        await message.answer("Доступ запрещен: у вас нет прав создателя предпросмотров.")
        return False
    return True

@router.message(Command(commands='submit_preview'))
async def submit_preview_command(message: Message):
    with SessionLocal() as db_session:
        db_repository = DatabaseRepository(db_session)
        if not await preview_maker_role_required(message, db_repository):
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
async def view_previews_command(message: Message):
    with SessionLocal() as db_session:
        db_repository = DatabaseRepository(db_session)
        if not await preview_maker_role_required(message, db_repository):
            return

        previews = PreviewsService(db_repository).get_previews_by_preview_maker_id(message.from_user.id)

        if not previews:
            await message.answer('You do not have any previews assigned to you.')
            return

        preview_messages = [f'{i+1}. {preview.video.title} (Deadline: {preview.deadline.strftime("%Y-%m-%d")})' for i, preview in enumerate(previews)]
        await message.answer('\n'.join(preview_messages))

@router.message(Command(commands='statistics'))
async def statistics_command(message: Message):
    with SessionLocal() as db_session:
        db_repository = DatabaseRepository(db_session)
        if not await preview_maker_role_required(message, db_repository):
            return

        total_previews = PreviewsService(db_repository).get_preview_maker_statistics(message.from_user.id)
        total_payment = PreviewsService(db_repository).get_preview_maker_payment(message.from_user.id)

        await message.answer(
            f'You have completed {total_previews} previews.\n'
            f'Your total payment for completed previews is {total_payment} USD.'
        )

def register_handlers(dp: Dispatcher):
    dp.include_router(router)