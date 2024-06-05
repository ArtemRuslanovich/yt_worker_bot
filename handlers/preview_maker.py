from aiogram import dp, types

from services.preview import PreviewsService
from services.statistics import StatisticsService

@dp.message_handler(lambda message: message.text.startswith('submit_preview') and StatisticsService.check_role(message.from_user, 'PreviewMaker'))
async def submit_preview_command(message: types.Message):
    user = message.from_user
    preview_id = int(message.text.split()[1])
    link = message.text.split()[2] if len(message.text.split()) > 2 else None

    if not preview_id or not link:
        await message.answer('Invalid preview submission. Please enter the preview ID and link in the following format: submit_preview <preview_id> <link>')
        return

    preview = PreviewsService.get_preview_by_id(preview_id)

    if not preview or preview.preview_maker_id != user.id or preview.status == 'completed':
        await message.answer('Invalid preview submission. You do not have a preview with the given ID or the preview has already been completed')
        return

    PreviewsService.update_preview(preview_id, 'completed', link)
    await message.answer(f'Preview for video "{preview.video.title}" has been submitted and is pending review')

@dp.message_handler(lambda message: message.text.startswith('view_previews') and StatisticsService.check_role(message.from_user, 'PreviewMaker'))
async def view_previews_command(message: types.Message):
    user = message.from_user
    previews = PreviewsService.get_previews_by_preview_maker_id(user.id)

    if not previews:
        await message.answer('You do not have any previews assigned to you')
        return

    preview_messages = [f'{i+1}. {preview.video.title} (Deadline: {preview.deadline.strftime("%Y-%m-%d")})' for i, preview in enumerate(previews)]
    await message.answer('\n'.join(preview_messages))

@dp.message_handler(lambda message: message.text.startswith('statistics') and StatisticsService.check_role(message.from_user, 'PreviewMaker'))
async def statistics_command(message: types.Message):
    user = message.from_user
    total_previews = StatisticsService.get_preview_maker_statistics(user.id)
    total_payment = PreviewsService.get_preview_maker_payment(user.id)

    await message.answer(
        f'You have completed {total_previews} previews.\n'
        f'Your total payment for completed previews is {total_payment} USD.'
    )