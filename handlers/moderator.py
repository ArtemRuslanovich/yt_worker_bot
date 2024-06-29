from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from keyboards.moderator_buttons import (
    moderator_main_keyboard, 
    channel_keyboard, 
    worker_keyboard, 
    task_keyboard, 
    question_keyboard, 
    worker_info_keyboard, 
    task_approval_keyboard
)
from database.database import Database

class ModeratorStates(StatesGroup):
    moderator = State()
    viewing_channels = State()
    viewing_workers = State()
    viewing_worker_info = State()
    adding_worker_expense = State()
    adding_worker_error = State()
    creating_story = State()
    viewing_questions = State()
    answering_question = State()
    sending_file = State()
    checking_task = State()
    entering_revision_message = State()

async def moderator_menu(message: types.Message, state: FSMContext):
    await message.answer("Меню модератора:", reply_markup=moderator_main_keyboard())
    await ModeratorStates.moderator.set()

async def view_channels(callback_query: types.CallbackQuery, state: FSMContext):
    db: Database = callback_query.bot['db']
    channels = await db.get_channels()
    await callback_query.message.answer("Список каналов:", reply_markup=channel_keyboard(channels))
    await ModeratorStates.viewing_channels.set()

async def view_workers(callback_query: types.CallbackQuery, state: FSMContext):
    db: Database = callback_query.bot['db']
    workers = await db.get_workers()
    await callback_query.message.answer("Список работников:", reply_markup=worker_keyboard(workers))
    await ModeratorStates.viewing_workers.set()

async def view_worker_info(callback_query: types.CallbackQuery, state: FSMContext):
    worker_id = int(callback_query.data.split("_")[2])
    db: Database = callback_query.bot['db']
    worker_info = await db.get_worker_monthly_info(worker_id)
    if not worker_info:
        await callback_query.message.answer("Информация о работнике не найдена.")
        return

    await state.update_data(worker_id=worker_id)
    channel_info = f"Канал: {worker_info.get('channel_name', 'N/A')}\n"
    await callback_query.message.answer(
        f"Информация о работнике:\n\n"
        f"Имя: {worker_info.get('username', 'N/A')}\n"
        f"Задания выполнены за месяц: {worker_info.get('monthly_tasks_completed', 'N/A')}\n"
        f"Ошибки за месяц: {worker_info.get('monthly_errors_made', 'N/A')}\n"
        f"Затраты: {worker_info.get('amount_spent', 'N/A')}\n"
        f"{channel_info}",
        reply_markup=worker_info_keyboard(add_back_button=True)
    )
    await ModeratorStates.viewing_worker_info.set()

async def add_worker_expense(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.message.answer("Введите сумму затрат:")
    await ModeratorStates.adding_worker_expense.set()

async def process_worker_expense(message: types.Message, state: FSMContext):
    try:
        amount = float(message.text)
        data = await state.get_data()
        worker_id = data['worker_id']
        db: Database = message.bot['db']
        await db.add_worker_expense(worker_id, amount)
        await message.answer(f"Затраты в размере {amount} успешно добавлены работнику.")
    except ValueError:
        await message.answer("Некорректный формат ввода. Введите число.")
    await moderator_menu(message, state)

async def add_worker_error(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.message.answer("Введите описание ошибки:")
    await ModeratorStates.adding_worker_error.set()

async def process_worker_error(message: types.Message, state: FSMContext):
    description = message.text
    data = await state.get_data()
    worker_id = data['worker_id']
    db: Database = message.bot['db']
    await db.add_worker_error(worker_id, description)
    await message.answer(f"Ошибка успешно добавлена работнику.")
    await moderator_menu(message, state)

async def create_story(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.message.answer("Введите текст сценария:")
    await ModeratorStates.creating_story.set()

async def process_story(message: types.Message, state: FSMContext):
    db: Database = message.bot['db']
    await db.create_story(message.text)
    await message.answer("Сценарий успешно создан.")
    await moderator_menu(message, state)

async def view_questions(callback_query: types.CallbackQuery, state: FSMContext):
    db: Database = callback_query.bot['db']
    questions = await db.get_questions()
    if questions:
        await callback_query.message.answer("Список вопросов:", reply_markup=question_keyboard(questions))
    else:
        await callback_query.message.answer("Нет вопросов.")
    await ModeratorStates.viewing_questions.set()

async def answer_question(callback_query: types.CallbackQuery, state: FSMContext):
    question_id = int(callback_query.data.split("_")[1])
    await state.update_data(question_id=question_id)
    await callback_query.message.answer("Введите ответ на вопрос:")
    await ModeratorStates.answering_question.set()

async def process_question_answer(message: types.Message, state: FSMContext):
    answer = message.text
    data = await state.get_data()
    question_id = data['question_id']
    db: Database = message.bot['db']
    await db.answer_question(question_id, answer)
    await message.answer("Ответ на вопрос отправлен.")
    await moderator_menu(message, state)

async def send_file(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.message.answer("Отправьте файл, который нужно переслать:")
    await ModeratorStates.sending_file.set()

async def process_file(message: types.Message, state: FSMContext):
    if message.document:
        file_id = message.document.file_id
        file_caption = message.caption or "Файл для вас"
        db: Database = message.bot['db']
        workers = await db.get_users_by_roles(['shooter', 'editor', 'preview_maker'])
        for worker in workers:
            try:
                await message.bot.send_document(worker['user_id'], file_id, caption=file_caption)
            except Exception as e:
                print(f"Не удалось отправить файл пользователю {worker['user_id']}: {e}")
        await message.answer("Файл успешно отправлен всем пользователям с ролями shooter, editor, preview_maker.")
    else:
        await message.answer("Пожалуйста, отправьте файл.")
    await moderator_menu(message, state)

async def view_tasks(callback_query: types.CallbackQuery, state: FSMContext):
    db: Database = callback_query.bot['db']
    tasks = await db.get_tasks()
    await callback_query.message.answer("Список всех задач:", reply_markup=task_keyboard(tasks))

async def check_task(callback_query: types.CallbackQuery, state: FSMContext):
    task_id = int(callback_query.data.split("_")[1])
    db: Database = callback_query.message.bot['db']
    task = await db.get_task_details(task_id)

    title = task.get('title', 'Без названия')
    description = task.get('description', 'Без описания')
    file_or_link = task.get('file_or_link', 'Нет прикрепленных файлов или ссылок.')
    worker_name = task.get('worker_name', 'Неизвестный работник')
    channel_name = task.get('channel_name', 'Неизвестный канал')
    revision_message = task.get('revision_message', 'Нет сообщений о доработке')

    await state.update_data(task_id=task_id)
    await callback_query.message.answer(
        f"Детали задачи:\n\n"
        f"Название: {title}\n"
        f"Описание: {description}\n"
        f"Канал: {channel_name}\n"
        f"Работник: {worker_name}\n"
        f"Прикрепленные файлы или ссылки: {file_or_link}\n"
        f"Сообщение о доработке: {revision_message}", 
        reply_markup=task_approval_keyboard(add_back_button=True)
    )
    await ModeratorStates.checking_task.set()

async def approve_task(callback_query: types.CallbackQuery, state: FSMContext):
    task_id = int((await state.get_data())['task_id'])
    db: Database = callback_query.bot['db']

    # Получаем информацию о задаче, чтобы узнать worker_id
    task_details = await db.get_task_details(task_id)
    worker_id = task_details['assigned_to']

    # Обновляем статус задачи на "approved"
    await db.update_task_status(task_id, 'approved')

    # Обновляем статистику задач для работника
    await db.update_task_completion(worker_id)

    await callback_query.message.answer("Задача одобрена.")
    await moderator_menu(callback_query.message, state)

async def revise_task(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.message.answer("Введите сообщение о доработке:")
    await ModeratorStates.entering_revision_message.set()

async def process_revision_message(message: types.Message, state: FSMContext):
    revision_message = message.text
    task_id = int((await state.get_data())['task_id'])
    db: Database = message.bot['db']
    await db.update_task_status(task_id, 'needs_revision')
    await db.update_task_revision_message(task_id, revision_message)
    task_details = await db.get_task_details(task_id)
    await db.add_worker_error(task_details['assigned_to'], f"Revision: {revision_message}")
    await message.answer("Задача отправлена на доработку с сообщением.")
    await moderator_menu(message, state)

def register_handlers(dp: Dispatcher):
    dp.register_message_handler(moderator_menu, commands=['moderator_menu'], state='*')
    dp.register_callback_query_handler(moderator_menu, lambda c: c.data == 'moderator_menu', state='*')
    dp.register_callback_query_handler(view_channels, lambda c: c.data == 'view_channels', state=ModeratorStates.moderator)
    dp.register_callback_query_handler(view_workers, lambda c: c.data == 'view_workers', state=ModeratorStates.moderator)
    dp.register_callback_query_handler(view_worker_info, lambda c: c.data.startswith('manage_worker_'), state=ModeratorStates.moderator)
    dp.register_callback_query_handler(add_worker_expense, lambda c: c.data == 'add_worker_expense', state=ModeratorStates.viewing_worker_info)
    dp.register_message_handler(process_worker_expense, state=ModeratorStates.adding_worker_expense)
    dp.register_callback_query_handler(add_worker_error, lambda c: c.data == 'add_worker_error', state=ModeratorStates.viewing_worker_info)
    dp.register_message_handler(process_worker_error, state=ModeratorStates.adding_worker_error)
    dp.register_callback_query_handler(create_story, lambda c: c.data == 'create_story', state=ModeratorStates.moderator)
    dp.register_message_handler(process_story, state=ModeratorStates.creating_story)
    dp.register_callback_query_handler(view_questions, lambda c: c.data == 'view_questions', state=ModeratorStates.moderator)
    dp.register_callback_query_handler(answer_question, lambda c: c.data.startswith('question_'), state=ModeratorStates.viewing_questions)
    dp.register_message_handler(process_question_answer, state=ModeratorStates.answering_question)
    dp.register_callback_query_handler(send_file, lambda c: c.data == 'send_file', state=ModeratorStates.moderator)
    dp.register_message_handler(process_file, content_types=types.ContentTypes.DOCUMENT, state=ModeratorStates.sending_file)
    dp.register_callback_query_handler(view_tasks, lambda c: c.data == 'view_tasks', state=ModeratorStates.moderator)
    dp.register_callback_query_handler(check_task, lambda c: c.data.startswith('task_'), state=ModeratorStates.moderator)
    dp.register_callback_query_handler(approve_task, lambda c: c.data == 'approve', state=ModeratorStates.checking_task)
    dp.register_callback_query_handler(revise_task, lambda c: c.data == 'revise', state=ModeratorStates.checking_task)
    dp.register_message_handler(process_revision_message, state=ModeratorStates.entering_revision_message)
