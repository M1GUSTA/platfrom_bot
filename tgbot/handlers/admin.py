import asyncpg
from aiogram import Router, types
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.methods import DeleteMessage, SendMessage
from aiogram.types import Message, ReplyKeyboardRemove

from tgbot.filters.admin import AdminFilter
from tgbot.keyboards.inline import get_edit_keyboard, get_check_keyboard, get_cancel_button, get_vote_keyboard
from tgbot.misc.states import Edit, Comment
from tgbot.services.db_base import db
import re

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

    print(title)
    try:
        proffer = await db.select_user_proffer(title=title)
        print(proffer)
    except Exception as ex:
        await callback.message.edit_text("Данное предложение уже изменено")
        return


    proffer = await db.select_user_proffer(id_proffer=proffer["id_proffer"])
    user = proffer["telegram_id"]
    action_admin = await db.select_action(telegram_id=str(admin), id_proffer=proffer["id_proffer"])
    if action_admin != None:
        if action_admin["telegram_id"]==str(admin):
            pass
        else:
            await callback.message.delete()
            await callback.message.answer(text="Данное предложение уже обрабатывается или обработано")
            return

    # await state.set_state(Edit.main)
    admin_id = await db.select_admin(telegram_id=str(admin))

    if action=="Edit":
        await db.update_proffer_status(7, proffer["id_proffer"])
        content = re.search(r"\n{2}(.+(\n.+)?){1,}.$", callback.message.text).group(1)
        await state.set_state(Edit.edit)
        await state.update_data(title=title, content=content, user=user, id_proffer=proffer["id_proffer"])
        await callback.message.edit_text("Чтобы вы хотели изменить?",
                                         reply_markup=get_edit_keyboard())

        await db.add_action(admin_id["id_admin"], 3, proffer["id_proffer"])


    elif action=="Comment":
        await db.update_proffer_status(7, proffer["id_proffer"])
        await state.set_state(Comment.comment)
        await state.update_data(msg1=callback.message.text, user=user, id_proffer=proffer["id_proffer"])
        await callback.message.edit_text("Напишите свой комментарий",
                                         reply_markup=get_cancel_button())
        msg_id = callback.message.message_id
        await state.update_data(msg=msg_id)
        await db.add_action(admin_id["id_admin"], 3, proffer["id_proffer"])



    elif action=="True":
        content = re.search(r"\n{2}(.+(\n.+)?){1,}.$", callback.message.text).group(1)
        await state.set_state(Edit.edit)
        await state.update_data(title=title, content=content, user=user)
        data = await state.get_data()
        users = await db.select_all_users()
        if proffer['comment']!=None:
            comment = f"Комментарий студсовета:\n{proffer['comment']}"
        else:
            comment = ""
        print(type(proffer['comment']), proffer['comment'])
        if proffer['anon']==False:
            fio = f"автор:{proffer['fio']}"
        else:
            fio = ""
        await db.update_proffer_status(2, proffer['id_proffer'])
        print(comment, fio)
        await callback.message.delete()
        for user in users:
            await SendMessage(chat_id=user["telegram_id"],
                              text=f"Новое предложение на голосовании!\n\n\n"
                                   f"{data['title']}\n\n"
                                   f"{data['content']}\n\n"
                                   f"{fio}\n"
                                   f"{comment}",
                              reply_markup=get_vote_keyboard())
        await db.add_action(admin_id["id_admin"], 1, proffer["id_proffer"])


    else:
        proffer_to_send= await db.select_user_proffer(id_proffer=proffer["id_proffer"])
        await callback.message.delete()
        if proffer_to_send["comment"]==None:
            try:
                await SendMessage(chat_id=proffer_to_send['telegram_id'],
                              text=f"Ваше предложение с темой\n"
                                   f"{proffer_to_send['title']}\n"
                                   f"Отклонено")
            except:
                pass
        else:
            try:
                await SendMessage(chat_id=proffer_to_send['telegram_id'],
                              text=f"Ваше предложение с темой\n"
                                   f"{proffer_to_send['title']}\n"
                                   f"Отклонено\n"
                                   f"Комментарий студсовета:\n"
                                   f"{proffer_to_send['comment']}")
            except:
                pass
        await db.update_proffer_status(id_status=6, id_proffer=proffer["id_proffer"])








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
    new_title = message.text
    if len(new_title) > 50:
        await message.answer("В заголовке должно быть не больше 50 символов")
    else:
        data = await state.get_data()
        await state.update_data(title=new_title)
        await message.delete()
        await DeleteMessage(chat_id=message.chat.id, message_id=data["msg"])
        await state.set_state(Edit.edit)
        await message.answer("Название обновлено, чтобы вы хотели изменить?",
                                         reply_markup=get_edit_keyboard())

@admin_router.message(Edit.content)
async def edit_title(message: types.Message, state: FSMContext):
    new_text = message.text
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
    current_state = await state.get_state()
    if current_state == "Comment:comment":
        data = await state.get_data()
        await callback.message.edit_text(text=data["msg1"],
                                         reply_markup=get_check_keyboard())
    else:
        await state.set_state(Edit.edit)
        await callback.message.edit_text("Чтобы вы хотели изменить?",
                                         reply_markup=get_edit_keyboard())

@admin_router.message(Comment.comment)
async def comment_add(message: types.Message, state: FSMContext):
    data = await state.get_data()
    comment = message.text
    await message.delete()
    await DeleteMessage(chat_id=message.chat.id, message_id=data["msg"])
    try:
        await db.update_proffer_comment(comment=comment, id_proffer=data["id_proffer"])
        await message.answer(f"Комментарий добавлен.\n"
                             f"{data['msg1']}",
                             reply_markup=get_check_keyboard())
        await state.clear()
    except:
        await message.answer("Возможно вы использовали неправильные символы.\n"
                                "Напишите свой комментарий еще раз",
                                reply_markup=get_cancel_button())
        await state.update_data(msg=message.message_id, comment=comment)

