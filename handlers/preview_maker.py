from aiogram import Router, types
from aiogram.filters import Command
from aiogram.types import Message

from services.preview import PreviewsService
from services.statistics import StatisticsService

router = Router()

@router.message(Command(commands='submit_preview'))
async def submit_preview_command(message: Message):
    if not StatisticsService.check_role(message.from_user, 'PreviewMaker'):
        return
    user = message.from_user
    text = message.text.split()
    preview_id = int(text[1]) if len(text) > 1 else None
    link = text[2] if len(text) > 2 else None

    if not preview_id or not link:
        await message.answer('Invalid preview submission. Please enter the preview ID and link in the following format: submit_preview <preview_id> <link>')
        return

    preview = PreviewsService.get_preview_by_id(preview_id)

    if not preview or preview.preview_maker_id != user.id or preview.status == 'completed':
        await message.answer('Invalid preview submission. You do not have a preview with the given ID or the preview has already been completed')
        return

    PreviewsService.update_preview(preview_id, 'completed', link)
    await message.answer(f'Preview for video "{preview.video.title}" has been submitted and is pending review')

@router.message(Command(commands='view_previews'))
async def view_previews_command(message: Message):
    if not StatisticsService.check_role(message.from_user, 'PreviewMaker'):
        return
    user = message.from_user
    previews = PreviewsService.get_previews_by_preview_maker_id(user.id)

    if not previews:
        await message.answer('You do not have any previews assigned to you')
        return

    preview_messages = [f'{i+1}. {preview.video.title} (Deadline: {preview.deadline.strftime("%Y-%m-%d")})' for i, preview in enumerate(previews)]
    await message.answer('\n'.join(preview_messages))

@router.message(Command(commands='statistics'))
async def statistics_command(message: Message):
    if not StatisticsService.check_role(message.from_user, 'PreviewMaker'):
        return
    user = message.from_user
    total_previews = StatisticsService.get_preview_maker_statistics(user.id)
    total_payment = PreviewsService.get_preview_maker_payment(user.id)

    await message.answer(
        f'You have completed {total_previews} previews.\n'
        f'Your total payment for completed previews is {total_payment} USD.'
    )
