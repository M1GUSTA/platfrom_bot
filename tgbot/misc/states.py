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
    main = State()

class Comment(StatesGroup):
    comment = State()

class ShowProffer(StatesGroup):
    start = State()