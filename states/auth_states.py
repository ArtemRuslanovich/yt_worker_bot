from aiogram.fsm.state import State, StatesGroup

class AuthStates(StatesGroup):
    waiting_for_role = State()
    waiting_for_username = State()
    waiting_for_password = State()
    admin = State()
    manager = State()
    moderator = State()
    shooter = State()
    editor = State()
    preview_maker = State()