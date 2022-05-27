import asyncpg
from aiogram import Router
from aiogram.dispatcher.filters import Text
from aiogram.types import Message, ReplyKeyboardRemove

from tgbot.filters.admin import AdminFilter
from tgbot.keyboards.reply import get_yes_no_kb
from tgbot.services.db_base import db

admin_router = Router()
admin_router.message.filter(AdminFilter())


# @admin_router.message(commands=["start"], state="*")
# async def admin_start(message: Message):
#     await message.reply("Приветствую, админ!")



@admin_router.message(commands=["start"])  # [2]
async def cmd_start(message: Message):
    await message.answer(
        "Вы довольны своей работой?",
        reply_markup=get_yes_no_kb()
    )

@admin_router.message(commands=["admins"])  # [2]
async def cmd_start(message: Message):
    try:
        admins = await db.select_all_admins()
    except asyncpg.exceptions.UniqueViolationError:
        pass
    admins_data = list(admins)
    print(admins_data)
    admins_name = admins_data[1]

    await message.answer(
        "\n".join([
            f'Список администраторов{admins_name}'
        ])
    )


@admin_router.message(Text(text="да", text_ignore_case=True))
async def answer_yes(message: Message):
    await message.answer(
        "Это здорово!",
        reply_markup=ReplyKeyboardRemove()
    )


@admin_router.message(Text(text="нет", text_ignore_case=True))
async def answer_no(message: Message):
    await message.answer(
        "Жаль...",
        reply_markup=ReplyKeyboardRemove()
    )
