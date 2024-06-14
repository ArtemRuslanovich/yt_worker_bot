from aiogram import Dispatcher, Router, types
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from database.repository import DatabaseRepository
from keyboards.moderator_buttons import get_moderator_keyboard
from services.expenses import ExpensesService
from services.statistics import StatisticsService
from database import SessionLocal

router = Router()

class ModeratorState(StatesGroup):
    waiting_for_channel_name = State()
    waiting_for_message_text = State()
    waiting_for_expense_amount = State()
    waiting_for_expense_currency = State()
    waiting_for_expense_channel_name = State()
    waiting_for_salary_username = State()
    waiting_for_salary_amount = State()

async def moderator_role_required(message: types.Message, db_repository):
    """Проверка, что пользователь имеет роль 'Moderator'."""
    if not StatisticsService(db_repository).check_role(message.from_user.id, 'Moderator'):
        await message.answer("Доступ запрещен: у вас нет прав модератора.")
        return False
    return True

@router.message(Command(commands='moderator'))
async def moderator_command(message: types.Message):
    with SessionLocal() as db_session:
        db_repository = DatabaseRepository(db_session)
        if not await moderator_role_required(message, db_repository):
            return

        await message.answer("Выберите действие:", reply_markup=get_moderator_keyboard())

@router.callback_query(lambda c: c.data in ['send_message', 'log_expense', 'set_salary'])
async def process_callback(callback_query: types.CallbackQuery, state: FSMContext):
    action = callback_query.data
    if action == 'send_message':
        await callback_query.message.answer("Введите название канала:")
        await state.set_state(ModeratorState.waiting_for_channel_name)
    elif action == 'log_expense':
        await callback_query.message.answer("Введите сумму расходов:")
        await state.set_state(ModeratorState.waiting_for_expense_amount)
    elif action == 'set_salary':
        await callback_query.message.answer("Введите имя пользователя работника:")
        await state.set_state(ModeratorState.waiting_for_salary_username)

@router.message(ModeratorState.waiting_for_channel_name)
async def process_channel_name(message: types.Message, state: FSMContext):
    await state.update_data(channel_name=message.text)
    await message.answer("Введите текст сообщения:")
    await state.set_state(ModeratorState.waiting_for_message_text)

@router.message(ModeratorState.waiting_for_message_text)
async def process_message_text(message: types.Message, state: FSMContext):
    data = await state.get_data()
    channel_name = data['channel_name']
    message_text = message.text

    with SessionLocal() as db_session:
        db_repository = DatabaseRepository(db_session)
        channel = db_repository.get_channel_by_name(channel_name)
        if not channel:
            await message.answer('Канал не найден.')
            return

        # Здесь предполагается интеграция с системой отправки сообщений
        # await bot.send_message(channel.telegram_id, message_text)
        await message.answer(f'Сообщение отправлено в {channel.name}')
    await state.clear()

@router.message(ModeratorState.waiting_for_expense_amount)
async def process_expense_amount(message: types.Message, state: FSMContext):
    try:
        amount = float(message.text)
        await state.update_data(expense_amount=amount)
        await message.answer("Введите валюту расходов (USD, RUB):")
        await state.set_state(ModeratorState.waiting_for_expense_currency)
    except ValueError:
        await message.answer('Неверный формат суммы. Пожалуйста, введите число.')

@router.message(ModeratorState.waiting_for_expense_currency)
async def process_expense_currency(message: types.Message, state: FSMContext):
    currency = message.text
    if currency not in ['USD', 'RUB']:
        await message.answer('Недопустимая валюта. Пожалуйста, используйте USD или RUB.')
        return
    await state.update_data(expense_currency=currency)
    await message.answer("Введите название канала для расходов:")
    await state.set_state(ModeratorState.waiting_for_expense_channel_name)

@router.message(ModeratorState.waiting_for_expense_channel_name)
async def process_expense_channel_name(message: types.Message, state: FSMContext):
    data = await state.get_data()
    channel_name = message.text
    with SessionLocal() as db_session:
        db_repository = DatabaseRepository(db_session)
        channel = db_repository.get_channel_by_name(channel_name)
        if not channel:
            await message.answer('Канал не найден.')
            return

        try:
            ExpensesService(db_repository).log_expense(
                message.from_user.id,
                data['expense_amount'],
                data['expense_currency'],
                channel.id
            )
            await message.answer(f'Расход в размере {data["expense_amount"]} {data["expense_currency"]} зарегистрирован для канала {channel.name}.')
        except Exception as e:
            await message.answer(f'Не удалось зарегистрировать расход: {str(e)}')
    await state.clear()

@router.message(ModeratorState.waiting_for_salary_username)
async def process_salary_username(message: types.Message, state: FSMContext):
    await state.update_data(salary_username=message.text)
    await message.answer("Введите сумму зарплаты:")
    await state.set_state(ModeratorState.waiting_for_salary_amount)

@router.message(ModeratorState.waiting_for_salary_amount)
async def process_salary_amount(message: types.Message, state: FSMContext):
    try:
        amount = float(message.text)
        data = await state.get_data()
        worker_username = data['salary_username']

        with SessionLocal() as db_session:
            db_repository = DatabaseRepository(db_session)
            worker = db_repository.get_user_by_username(worker_username)

            if not worker:
                await message.answer('Работник не найден.')
                return

            db_repository.set_worker_salary(worker.id, amount)
            await message.answer(f'Зарплата для {worker.username} установлена в размере {amount} USD за задачу.')
    except ValueError:
        await message.answer('Пожалуйста, введите корректное числовое значение для суммы.')
    await state.clear()

def register_handlers(dp: Dispatcher):
    dp.include_router(router)