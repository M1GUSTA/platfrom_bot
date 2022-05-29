import re

import aiogram
from aiogram import Router, types
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.methods import SendMessage
from aiogram.types import Message

from tgbot import config
from tgbot.handlers.data.bw import bad_words
from tgbot.keyboards.inline import get_anon_keyboard, get_prof_keyboard, get_prof_keyboard1, get_check_keyboard
from tgbot.keyboards.reply import get_user_kb, get_phone_button
from tgbot.misc.states import NotAuthorised, Proffer
from tgbot.services.db_base import db

user_router = Router()
from tgbot.config import Config


@user_router.message(commands=["start"])
async def user_start(message: Message, state: FSMContext):
    user = str(message.from_user.id)
    check = await db.select_user(telegram_id=user)
    if check==None:
        await state.set_state(NotAuthorised.authorization)
        await message.answer("Приветствую! Что бы вы хотели сделать? \n",
                             reply_markup=get_user_kb())
    else:
        await message.answer("Приветствую! Что бы вы хотели сделать? \n",
                             reply_markup=get_user_kb())



@user_router.message(commands=["help"])
async def user_start(message: Message):
    text= "создан"
    await message.answer(f"Данный бот {text} для проведения голосований \n"
                        f"за предложения учащихся РГУ Косыгина.\n"
                        f"Чтобы сделать предложение вам нужно авторизоваться\n"
                        f"на платформе голосований.\n",
                        )


@user_router.message(Text(text="Написать предложение"))
async def make_proffer(message: types.Message, state: FSMContext):
    await state.clear()
    user = str(message.from_user.id)
    check = await db.select_user(telegram_id=user)
    if check != None:
        await state.set_state(Proffer.title)
        await message.answer("Напишите заголовок, он должен быть не длиннее 50 символов.")
        await state.update_data(user=check['id_user'])
    else:
        await message.answer("Только авторизованные пользователи могут создавать\n"
                            "предложения.\nЧтобы проверить вашу авторизацию "
                            "нажмите на кнопку ниже и согласитесь на проверку по номеру телефона",
                            reply_markup=get_phone_button())


@user_router.message(Proffer.title)
async def set_content(message: Message, state: FSMContext) -> None:
    title_text = message.text
    check = False
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
            await state.set_state(Proffer.content)
            await message.answer("Теперь опишите развернуто,\n"
                                     "что бы вы хотели предложить. \n"
                                 "Он должен быть не длиннее 300 символов.")


@user_router.message(Proffer.content)
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


            await message.answer("Почти готово, ваше предложение будет отправлено на рассмотрение студсоветом."
                                 "Как вы хотите его отправить?",
                                 reply_markup=get_anon_keyboard())


@user_router.callback_query(Text(text_startswith="anon"), Proffer.content)
async def send_proffer(callback: types.CallbackQuery, state: FSMContext, config: Config):
    action = callback.data.split("_")[1]
    user = callback.from_user.id
    await state.update_data(anon=action)
    data = await state.get_data()
    await db.add_proffer(content=data["content"], anon=bool(data["anon"]), id_user=int(data["user"]), id_status=1, title=data["title"])
    print(config.tg_bot.admin_ids)
    print(data)
    for admin in config.tg_bot.admin_ids:
        # if bool(data["anon"])==True:
        await SendMessage(chat_id=admin,text=f"Пришло новое предложение!\n\n\n"
                                                 f"{data['title']}\n\n"
                                                 f"{data['content']}",
                              reply_markup=get_check_keyboard())
    await callback.answer("Предложение на рассмотрении")
    await state.clear()



@user_router.message(content_types=types.ContentType.CONTACT)
async def get_contact(message: types.Message):
    contact = str(message.contact)
    check = await db.select_user(telegram_id=contact)
    if check != None:
        pass
    else:
        await message.answer("Вы должны авторизоваться на платформе",
                             reply_markup=get_user_kb())


@user_router.message(Text(text="Просмотреть предложения"))
async def show_menu(message: types.Message, state: FSMContext):
    await state.clear()
    user = str(message.from_user.id)
    # print(user)
    check = await db.select_user_proffer(telegram_id=user)
    # print(check)
    if check != None:
        await message.answer("Вы можете выбрать какие предложения вы хотите просмотреть\n",
                            reply_markup=get_prof_keyboard1())
    else:
        await message.answer("Вы можете выбрать какие предложения вы хотите просмотреть\n",
                             reply_markup=get_prof_keyboard1())

@user_router.callback_query(Text(text_startswith="show"))
async def show_proffer(callback: types.CallbackQuery, state: FSMContext):
    action = callback.data.split("_")[1]
    if action == "vote":
        pass