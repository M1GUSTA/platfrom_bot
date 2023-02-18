import logging
import re
from datetime import datetime

import aiogram
from aiogram import Router, types
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.methods import SendMessage, DeleteMessage
from aiogram.types import Message

from tgbot import config
from tgbot.handlers.data.bw import bad_words
from tgbot.keyboards.inline import get_anon_keyboard, get_prof_keyboard1, get_check_keyboard, get_cancel_button, \
    pagination_keyboard, vote_pagination_keyboard
from tgbot.keyboards.reply import get_user_kb, get_phone_button
from tgbot.misc.states import NotAuthorised, Proffer, ShowProffer
from tgbot.services.db_base import db

user_router = Router()
from tgbot.config import Config
flags = {"throttling_key": "default"}


@user_router.message(commands=["start"], flags=flags)
async def user_start(message: Message, state: FSMContext):
    await state.clear()
    user = str(message.from_user.id)
    check = await db.select_user(telegram_id=user)
    if check==None:
        await state.set_state(NotAuthorised.authorization)
        await message.answer("Приветствую! Что бы вы хотели сделать? \n",
                             reply_markup=get_user_kb())
    else:
        await message.answer("Приветствую! Что бы вы хотели сделать? \n",
                             reply_markup=get_user_kb())



@user_router.message(commands=["help"], flags=flags)
async def user_start(message: Message):
    text= "создан"
    await message.answer(f"Данный бот {text} для проведения голосований \n"
                        f"за предложения учащихся РГУ Косыгина.\n"
                        f"Чтобы сделать предложение вам нужно авторизоваться\n"
                        f"на платформе голосований.\n",
                        )


@user_router.message(Text(text="Написать предложение"), flags=flags)
async def make_proffer(message: types.Message, state: FSMContext):
    await state.clear()
    user = str(message.from_user.id)
    check = await db.select_user(telegram_id=user)
    if check != None:
        await state.set_state(Proffer.title)
        await message.answer("Напишите заголовок, он должен быть не длиннее 50 символов.")
        # msg = [message.message_id]
        # await state.update_data(msg=msg)
        await state.update_data(user=check['id_user'])
    else:
        await message.answer("Только авторизованные пользователи могут создавать\n"
                            "предложения.\nЧтобы проверить вашу авторизацию "
                            "нажмите на кнопку ниже и согласитесь на проверку по номеру телефона",
                            reply_markup=get_phone_button())
        # await state.set_state()


@user_router.message(Proffer.title, flags=flags)
async def set_content(message: Message, state: FSMContext) -> None:
    title_text = message.text
    check = False
    if title_text=="Просмотреть предложения":
        await state.clear()
        await message.answer("Заполнение предложения отменено")
        return
    if len(title_text) > 50:
        await message.answer("В заголовке должно быть не больше 50 символов")
    else:
        for i in bad_words:
            if re.search(i, title_text):
                check = True
                break
        if check ==True:
            await message.answer("В названии присутсвуют нецензурные слова или символы.\n"
                                 "Напишите другое название.")
        else:
            await state.update_data(title=message.text)
            # data = await state.get_data()
            # msg = data["msg"].append()
            # await state.update_data(msg=msg)
            await state.set_state(Proffer.content)
            await message.answer("Теперь опишите развернуто,\n"
                                     "что бы вы хотели предложить. \n"
                                 "Текст должен быть не длиннее 300 символов.")


@user_router.message(Proffer.content, flags=flags)
async def proffer_check(message: Message, state: FSMContext) -> None:
    check = False
    content_text = message.text
    if len(content_text) > 300:
        await message.answer("В тексте должно быть не больше 300 символов")
    else:
        for i in bad_words:
            if re.search(i, content_text):
                check = True
                break
        if check == True:
            await message.answer("В тексте присутсвуют нецензурные слова или символы.\n"
                                 "Напишите свое предложение другими словами.")
        else:
            await state.update_data(content=f"{content_text}.")
            # data = await state.get_data()
            # msg = data["msg"].append()
            # await state.update_data(msg=msg)
            await message.answer("Почти готово, ваше предложение будет отправлено на рассмотрение студсоветом."
                                 "Как вы хотите его отправить?",
                                 reply_markup=get_anon_keyboard())


@user_router.callback_query(Text(text_startswith="anon"), Proffer.content, flags=flags)
async def send_proffer(callback: types.CallbackQuery, state: FSMContext, config: Config):
    action = callback.data.split("_")[1]
    # user = callback.from_user.id
    await state.update_data(anon=action)
    data = await state.get_data()
    await db.add_proffer(content=data["content"], anon=(data["anon"]=='True'), id_user=int(data["user"]), id_status=1, title=data["title"])
    print(data['anon']=='True')
    print(config.tg_bot.admin_ids)
    print(data)
    await callback.message.delete()
    for admin in config.tg_bot.admin_ids:
        # if bool(data["anon"])==True:
        await SendMessage(chat_id=admin,text=f"Пришло новое предложение!\n\n\n"
                                                 f"{data['title']}\n\n"
                                                 f"{data['content']}",
                              reply_markup=get_check_keyboard())
    await callback.answer("Предложение на рассмотрении")
    await state.clear()



@user_router.message(content_types=types.ContentType.CONTACT, flags=flags)
async def get_contact(message: types.Message, state: FSMContext):
    contact = str(message.contact.phone_number)
    print(contact)
    check = await db.select_user(phone=contact)
    if check != None:
            await db.update_user(str(message.from_user.id), contact)
            await message.delete()
            await state.set_state(Proffer.title)
            await message.answer("Напишите заголовок, он должен быть не длиннее 50 символов.",
                                 reply_markup=get_user_kb())
            # msg = [message.message_id]
            # await state.update_data(msg=msg)
            await state.update_data(user=check['id_user'])
    else:
        await message.answer("Вы должны авторизоваться на платформе",
                             reply_markup=get_user_kb())




@user_router.message(Text(text="Просмотреть предложения"), flags=flags)
async def show_menu(message: types.Message, state: FSMContext):
    await state.clear()
    await state.set_state(ShowProffer.start)
    user = str(message.from_user.id)

    # print(user)
    # check = await db.select_user_proffer(telegram_id=user)
    # print(check)
    await message.answer("Вы можете выбрать какие предложения вы хотите просмотреть\n",
                        reply_markup=get_prof_keyboard1())
    msg = message.message_id
    await state.update_data(message_id=msg)



@user_router.message(ShowProffer.start, flags=flags)
async def delete_msg(message: types.Message, state:FSMContext):
    data = await state.get_data()
    await DeleteMessage(chat_id=message.chat.id, message_id=data["message_id"])
    await state.clear()




@user_router.callback_query(Text(text_startswith="show"), flags=flags)
async def show_proffer(callback: types.CallbackQuery, state: FSMContext):
    action = callback.data.split("_")[1]
    if action == "vote":
        prof_list = await db.select_all_proffers(id_status=2)
        await state.update_data(prof_list=prof_list, cur_prof=0, vote=True)
        print(prof_list)
        proffer = prof_list[0]
        if proffer["comment"] == None:
            comment = "oтсутствует"
        else:
            comment = proffer["comment"]
        if proffer['rating1'] == None:
            rating1 = 0
        else:
            rating1 = proffer['rating1']
        if proffer['rating2'] == None:
            rating2 = 0
        else:
            rating2 = proffer['rating2']
        await callback.message.edit_text(f"{proffer['title']}\n\n"
                                         f"{proffer['content']}\n\n"
                                         f"Комментарий Студсовета \n"
                                         f"{comment}\n"
                                         f"🔥{rating1} 😖{rating2}",
                                         reply_markup=vote_pagination_keyboard())
    elif action == "proc":
        prof_list = await db.select_all_proffers(id_status=3)
        try:
            proffer = prof_list[0]
        except:
            callback.answer()
            return
        await state.update_data(prof_list=prof_list, cur_prof=0, vote=False)
        if proffer["comment"] == None:
            comment = "oтсутствует"
        else:
            comment = proffer["comment"]
        if proffer['rating1'] == None:
            rating1 = 0
        else:
            rating1 = proffer['rating1']
        if proffer['rating2'] == None:
            rating2 = 0
        else:
            rating2 = proffer['rating2']
        await callback.message.edit_text(f"{proffer['title']}\n\n"
                                         f"{proffer['content']}\n\n"
                                         f"Комментарий Студсовета \n"
                                         f"{comment}\n"
                                         f"🔥{rating1} 😖{rating2}",
                                         reply_markup=pagination_keyboard())
    elif action == "complete":
        prof_list = await db.select_all_proffers(id_status=4)
        try:
            proffer = prof_list[0]
        except:
            callback.answer()
            return
        await state.update_data(prof_list=prof_list, cur_prof=0, vote=False)
        if proffer["comment"] == None:
            comment = "oтсутствует"
        else:
            comment = proffer["comment"]
        if proffer['rating1'] == None:
            rating1 = 0
        else:
            rating1 = proffer['rating1']
        if proffer['rating2'] == None:
            rating2 = 0
        else:
            rating2 = proffer['rating2']
        await callback.message.edit_text(f"{proffer['title']}\n\n"
                                         f"{proffer['content']}\n\n"
                                         f"Комментарий Студсовета \n"
                                         f"{comment}\n"
                                         f"🔥{rating1} 😖{rating2}",
                                         reply_markup=pagination_keyboard())
    elif action == "reject":
        prof_list = await db.select_all_proffers(id_status=5)
        try:
            proffer = prof_list[0]
        except:
            callback.answer()
            return
        await state.update_data(prof_list=prof_list, cur_prof=0, vote=False)
        if proffer["comment"] == None:
            comment = "oтсутствует"
        else:
            comment = proffer["comment"]
        if proffer['rating1'] == None:
            rating1 = 0
        else:
            rating1 = proffer['rating1']
        if proffer['rating2'] == None:
            rating2 = 0
        else:
            rating2 = proffer['rating2']
        await callback.message.edit_text(f"{proffer['title']}\n\n"
                                         f"{proffer['content']}\n\n"
                                         f"Комментарий Студсовета \n"
                                         f"{comment}\n"
                                         f"🔥{rating1} 😖{rating2}",
                                         reply_markup=pagination_keyboard())
    else:
        await callback.message.delete()

@user_router.callback_query(Text(text_startswith="prof"),ShowProffer.start)
async def change_prof(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer(cache_time=1)
    action = callback.data.split("_")[1]
    data = await state.get_data()
    current_prof = data["cur_prof"]
    prof_list = data["prof_list"]
    if action == "previous":
        current_prof -= 1
        await state.update_data(cur_prof=current_prof)
        try:
            proffer = prof_list[current_prof]
        except:
            proffer = prof_list[-1]
            current_prof = -1
            await state.update_data(cur_prof=current_prof)
        if proffer["comment"]==None:
            comment = "oтсутствует"
        else:
            comment = proffer["comment"]
        if proffer['rating1']==None:
            rating1 = 0
        else:
            rating1 = proffer['rating1']
        if proffer['rating2']==None:
            rating2=0
        else:
            rating2=proffer['rating2']
        if data['vote']:
            keyboard=vote_pagination_keyboard()
        else:
            keyboard=pagination_keyboard()
        await callback.message.edit_text(f"{proffer['title']}\n\n"
                                         f"{proffer['content']}\n\n"
                                         f"Комментарий Студсовета \n"
                                         f"{comment}\n"
                                         f"🔥{rating1} 😖{rating2}",
                                         reply_markup=keyboard)
    elif action == "next":
        current_prof += 1
        await state.update_data(cur_prof=current_prof)
        try:
            proffer = prof_list[current_prof]
        except:
            proffer= prof_list[0]
            current_prof = 0
            await state.update_data(cur_prof=current_prof)
        if proffer["comment"]==None:
            comment ="Отсутствует"
        else:
            comment = proffer["comment"]
        if proffer['rating1']==None:
            rating1 = 0
        else:
            rating1 = proffer['rating1']
        if proffer['rating2']==None:
            rating2=0
        else:
            rating2=proffer['rating2']
        if data['vote']:
            keyboard=vote_pagination_keyboard()
        else:
            keyboard=pagination_keyboard()
        await callback.message.edit_text(f"{proffer['title']}\n\n"
                                         f"{proffer['content']}\n\n"
                                         f"Комментарий Студсовета\n"
                                         f"{comment}\n"
                                         f"🔥{rating1} 😖{rating2}",
                                         reply_markup=keyboard)
    else:
        await callback.message.edit_text("Вы можете выбрать какие предложения вы хотите просмотреть\n",
                             reply_markup=get_prof_keyboard1())

@user_router.callback_query(Text(text_startswith="vote"), ShowProffer.start)
async def change_prof(callback: types.CallbackQuery, state: FSMContext):
    action = callback.data.split("_")[1]
    try:
        title = re.search(r"\n{3}(.+)\n{2}", callback.message.text).group(1)
        proffer = await db.select_user_proffer(title=title)
    except:
        data =await state.get_data()
        prof_list = data["prof_list"]
        current_prof = data["cur_prof"]
        proffer = prof_list[current_prof]
    print(proffer)
    user_id = await db.select_user(telegram_id=str(callback.from_user.id))
    if user_id==None:
        await callback.answer("Вы не авторизованы")
    rating = await db.select_rating_prof(id_proffer=proffer['id_proffer'], id_user=user_id["id_user"])
    print(rating)
    if rating == None:
        if (action=="positive"):
            await db.add_rating(decision=True, id_proffer=proffer['id_proffer'], id_user=user_id["id_user"])
        if (action=="negative"):
            await db.add_rating(decision=False, id_proffer=proffer['id_proffer'], id_user=user_id["id_user"])
        await callback.answer("Рейтинг изменен")
    else:
        if (action=="positive"):
            await db.update_rating(decision=True, date_zapis=datetime.now().date(), id_zapis=rating["id_zapis"])
        if (action=="negative"):
            await db.update_rating(decision=False, date_zapis=datetime.now().date(), id_zapis=rating["id_zapis"])
        await callback.answer("Рейтинг изменен")




@user_router.callback_query(Text(text_startswith="vote"))
async def change_prof(callback: types.CallbackQuery):
    action = callback.data.split("_")[1]
    title = re.search(r"\n{3}(.+)\n{2}", callback.message.text).group(1)
    user_id = await db.select_user(telegram_id=str(callback.from_user.id))
    if user_id == None:
        await callback.answer("Вы не авторизованы")
    proffer = await db.select_user_proffer(title=title)
    if (action == "positive"):
        await db.add_rating(decision=True, id_proffer=proffer['id_proffer'], id_user=user_id["id_user"])
        await callback.message.delete()
    if (action == "negative"):
        await db.add_rating(decision=False, id_proffer=proffer['id_proffer'], id_user=user_id["id_user"])
        await callback.message.delete()