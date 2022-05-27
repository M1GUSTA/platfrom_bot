from aiogram.dispatcher.fsm.state import StatesGroup, State


class NotAuthorised(StatesGroup):
    authorization = State()

class Proffer(StatesGroup):
    title = State()
    content = State()
