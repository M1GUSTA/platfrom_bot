from aiogram.dispatcher.fsm.state import StatesGroup, State


class NotAuthorised(StatesGroup):
    authorization = State()

class Proffer(StatesGroup):
    title = State()
    content = State()

class Edit(StatesGroup):
    edit = State()
    title = State()
    content = State()
