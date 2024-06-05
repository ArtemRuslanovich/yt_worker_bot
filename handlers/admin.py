from aiogram import dp, types

from services.channels import ChannelsService
from services.expenses import ExpensesService
from services.payment import PaymentService
from services.statistics import StatisticsService

@dp.message_handler(lambda message: message.text.startswith('create_channel') and StatisticsService.check_role(message.from_user, 'Admin'))
async def create_channel_command(message: types.Message):
    user = message.from_user
    name = message.text.split()[1]

    if not name:
        await message.answer('Invalid channel creation. Please enter the channel name in the following format: create_channel <name>')
        return

    channel = ChannelsService.create_channel(name, user.id)
    await message.answer(f'Channel "{channel.name}" has been created and you have been assigned as the manager')

@dp.message_handler(lambda message: message.text.startswith('view_channels') and StatisticsService.check_role(message.from_user, 'Admin'))
async def view_channels_command(message: types.Message):
    user = message.from_user
    channels = ChannelsService.get_channels_by_manager_id(user.id)

    if not channels:
        await message.answer('You do not have any channels assigned to you')
        return

    channel_messages = [f'{i+1}. {channel.name} (Total expenses: {channel.total_expenses} USD, Total payments: {channel.total_payments} USD)' for i, channel in enumerate(channels)]
    await message.answer('\n'.join(channel_messages))

@dp.message_handler(lambda message: message.text.startswith('statistics') and StatisticsService.check_role(message.from_user, 'Admin'))
async def statistics_command(message: types.Message):
    user = message.from_user
    channels = ChannelsService.get_channels_by_manager_id(user.id)
    total_expenses = 0
    total_payments = 0

    for channel in channels:
        total_expenses += channel.total_expenses
        total_payments += channel.total_payments

    await message.answer(
        f'You have {len(channels)} channels under your management.\n'
        f'Total expenses for all channels: {total_expenses} USD.\n'
        f'Total payments for all channels: {total_payments} USD.'
    )

@dp.message_handler(lambda message: message.text.startswith('log_expense') and StatisticsService.check_role(message.from_user, 'Admin'))
async def log_expense_command(message: types.Message):
    user = message.from_user
    amount = float(message.text.split()[1])
    description = message.text.split()[2] if len(message.text.split()) > 2 else None
    channel_id = int(message.text.split()[3]) if len(message.text.split()) > 3 else user.channel_id

    if not amount or (amount <= 0) or not description:
        await message.answer('Invalid expense logging. Please enter the amount, description, and channel ID in the following format: log_expense <amount> <description> [<channel_id>]')
        return

    expense = ExpensesService.log_expense(amount, description, channel_id)
    await message.answer(f'Expense of {amount} USD for "{description}" has been logged for channel {expense.channel.name}')

@dp.message_handler(lambda message: message.text.startswith('log_payment') and StatisticsService.check_role(message.from_user, 'Admin'))
async def log_payment_command(message: types.Message):
    user = message.from_user
    amount = float(message.text.split()[1])
    description = message.text.split()[2] if len(message.text.split()) > 2 else None
    channel_id = int(message.text.split()[3]) if len(message.text.split()) > 3 else user.channel_id

    if not amount or (amount <= 0) or not description:
        await message.answer('Invalid payment logging. Please enter the amount, description, and channel ID in the following format: log_payment <amount> <description> [<channel_id>]')
        return

    payment = PaymentService.log_payment(amount, description, channel_id)
    await message.answer(f'Payment of {amount} USD for "{description}" has been logged for channel {payment.channel.name}')