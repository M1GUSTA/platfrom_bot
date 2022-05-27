from aiogram import types
from aiogram.types import ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder



def get_yes_no_kb() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.button(text="Да")
    kb.button(text="Нет")
    kb.adjust(2)
    return kb.as_markup(resize_keyboard=True)

def get_phone_button() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.row(types.KeyboardButton(text="Проверить", request_contact=True))
    builder.adjust(1)
    keyboard = builder.as_markup(resize_keyboard=True)
    return keyboard

def get_user_kb() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.button(text="Просмотреть предложения")
    kb.button(text="Написать предложение")
    kb.adjust(2)
    return kb.as_markup(resize_keyboard=True)

