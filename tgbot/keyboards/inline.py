from aiogram import types
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_phone_button() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="Проверить", request_contact=True,
                                           callback_data="phone"))
    keyboard = builder.as_markup()
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
