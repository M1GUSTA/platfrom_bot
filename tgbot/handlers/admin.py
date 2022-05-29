import asyncpg
from aiogram import Router, types
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.methods import DeleteMessage
from aiogram.types import Message, ReplyKeyboardRemove
import re

from tgbot.filters.admin import AdminFilter
from tgbot.keyboards.inline import get_edit_keyboard, get_check_keyboard, get_cancel_button
from tgbot.misc.states import Edit
from tgbot.services.db_base import db

admin_router = Router()
admin_router.message.filter(AdminFilter())


# @admin_router.message(commands=["start"], state="*")
# async def admin_start(message: Message):
#     await message.reply("Приветствую, админ!")


@admin_router.message(commands=["admins"])  # [2]
async def cmd_start(message: Message):
    try:
        admins = await db.select_all_admins()
    except asyncpg.exceptions.UniqueViolationError:
        pass
    admins_data = list(admins)
    admins_name = admins_data[1]

    await message.answer(
        "\n".join([
            f'Список администраторов{admins_name}'
        ])
    )


@admin_router.callback_query(Text(text_startswith="check"))
async def proffer_processing(callback: types.CallbackQuery, state: FSMContext):
    action = callback.data.split("_")[1]
    admin = callback.from_user.id
    title = re.search(r"\n{3}(.+)\n{2}", callback.message.text, re.DOTALL).group(1)


    try:
        proffer =await db.select_user_proffer(title=title)
    except Exception as ex:
        await callback.message.edit_text("Данное предложение уже изменено")
        return


    proffer = await db.select_user_proffer(id_proffer=proffer["id_proffer"])
    user = proffer["telegram_id"]
    action_admin = await db.select_action(telegram_id=str(admin), id_proffer=proffer["id_proffer"])
    print(action_admin)
    if action_admin != None:
        await callback.message.answer("Данное предложение уже обрабатывается или обработано")
        return

    await db.update_proffer_status(7, proffer["id_proffer"])
    admin_id = await db.select_admin(telegram_id=str(admin))

    if action=="Edit":
        content = re.search(r"\n{2}(.+(\n.+)?){1,}.$", callback.message.text).group(1)
        await state.set_state(Edit.edit)
        await state.update_data(title=title, content=content, user=user, id_proffer=proffer["id_proffer"])
        await callback.message.edit_text("Чтобы вы хотели изменить?",
                                         reply_markup=get_edit_keyboard())

        await db.add_action(admin_id["id_admin"], 3, proffer["id_proffer"])

    elif action=="Comment":
        await callback.message.edit_text("")


    elif action=="True":
        pass


    else:
        pass

@admin_router.callback_query(Text(text_startswith="edit"), Edit.edit)
async def edit_process(callback: types.CallbackQuery, state: FSMContext):
    data =await state.get_data()

    action = callback.data.split("_")[1]
    user = callback.from_user.id
    if action =="title":
        title=data["title"]
        await state.set_state(Edit.title)
        await callback.message.edit_text(f"Напишите исправленный заголовок.\n"
                                      f"<code>{title}</code>\n"
                                      f"<i>(вы можете скопировать исходный текст нажав на него)</i>",
                                         reply_markup=get_cancel_button())
        msg_id = callback.message.message_id
        print(msg_id)
        await state.update_data(msg=msg_id)
    elif action=="content":
        content = data["content"]
        await state.set_state(Edit.content)
        await callback.message.edit_text(f"Напишите исправленный текст.\n"
                                      f"<code>{content}</code>\n"
                                      f"<i>(вы можете скопировать исходный текст нажав на него)</i>",
                                         reply_markup=get_cancel_button())
        msg_id = callback.message.message_id
        await state.update_data(msg=msg_id)
    else:
        await state.clear()
        await db.update_proffer(content=data["content"], title=data["title"], id_proffer=int(data["id_proffer"]))
        await callback.message.edit_text(text=f"Пришло новое предложение!\n\n\n"
                                                 f"{data['title']}\n\n"
                                                 f"{data['content']}",
                                         reply_markup=get_check_keyboard())

@admin_router.message(Edit.title)
async def edit_title(message: types.Message, state: FSMContext):
    user_msg = message.message_id
    new_title = message.text
    if len(new_title) > 50:
        await message.answer("В заголовке должно быть не больше 50 символов")
    else:
        data = await state.get_data()
        print(data["msg"])
        await state.update_data(title=new_title)
        await message.delete()
        await DeleteMessage(chat_id=message.chat.id, message_id=data["msg"])
        await state.set_state(Edit.edit)
        await message.answer("Название обновлено, чтобы вы хотели изменить?",
                                         reply_markup=get_edit_keyboard())

@admin_router.message(Edit.content)
async def edit_title(message: types.Message, state: FSMContext):
    new_text = message.text
    user_msg = message.message_id
    if len(new_text) > 300:
        await message.answer("В текстке должно быть не больше 300 символов")
    else:
        data = await state.get_data()
        await state.update_data(content=new_text)
        await message.delete()
        await DeleteMessage(chat_id=message.chat.id, message_id=data["msg"])
        await state.set_state(Edit.edit)
        await message.answer("Содержание обновлено, чтобы вы хотели изменить?",
                                         reply_markup=get_edit_keyboard())

@admin_router.callback_query(Text(text="cancel"))
async def go_back(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(Edit.edit)
    await callback.message.edit_text("Чтобы вы хотели изменить?",
                                     reply_markup=get_edit_keyboard())

