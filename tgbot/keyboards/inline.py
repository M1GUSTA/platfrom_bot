from aiogram import types
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_phone_button() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="Проверить", request_contact=True,
                                           callback_data="phone"))
    keyboard = builder.as_markup()
    return keyboard

def get_check_keyboard() -> InlineKeyboardMarkup:
    buttons= [
        [
            types.InlineKeyboardButton(text="Отправить на голосование", callback_data="check_True"),
            types.InlineKeyboardButton(text="В спам", callback_data="check_False")
        ],
        [
            types.InlineKeyboardButton(text="Редактировать", callback_data="check_Edit"),
            types.InlineKeyboardButton(text="Комментировать", callback_data="check_Comment")
        ]
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons, resize_keyboard=True)
    return keyboard


def get_anon_keyboard():
    buttons = [
        [
            types.InlineKeyboardButton(text="Анонимно", callback_data="anon_True"),
            types.InlineKeyboardButton(text="Не анонимно", callback_data="anon_False")
        ],
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons, resize_keyboard=True)
    return keyboard

def get_prof_keyboard():
    buttons = [
        [
            types.InlineKeyboardButton(text="На голосовании", callback_data="show_vote"),
            types.InlineKeyboardButton(text="В процессе", callback_data="show_prof")
        ],
        [
            types.InlineKeyboardButton(text="Выполненные", callback_data="show_prof"),
            types.InlineKeyboardButton(text="Отклоненные", callback_data="show_prof")
        ]
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons, resize_keyboard=True)
    return keyboard

def get_prof_keyboard1():
    buttons = [
        [
            types.InlineKeyboardButton(text="На голосовании", callback_data="show_vote"),
            types.InlineKeyboardButton(text="В процессе", callback_data="show_proc")
        ],
        [
            types.InlineKeyboardButton(text="Выполненные", callback_data="show_complete"),
            types.InlineKeyboardButton(text="Отклоненные", callback_data="show_reject")
        ],
        [
            types.InlineKeyboardButton(text="Мои предложения", callback_data="show_mine")
        ]
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons, resize_keyboard=True)
    return keyboard

def get_edit_keyboard():
    buttons = [
        [
            types.InlineKeyboardButton(text="Название", callback_data="edit_title"),
            types.InlineKeyboardButton(text="Содержание", callback_data="edit_content")
        ],
        [
            types.InlineKeyboardButton(text="Назад", callback_data="edit_cancel")
        ]
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons, resize_keyboard=True)
    return keyboard

def get_cancel_button():
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="Отмена",
                                           callback_data="cancel"))
    keyboard = builder.as_markup()
    return keyboard