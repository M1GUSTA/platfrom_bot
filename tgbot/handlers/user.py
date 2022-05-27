import re

from aiogram import Router, types
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.types import Message

from tgbot.handlers.data.bw import bad_words
from tgbot.keyboards.inline import get_anon_keyboard
from tgbot.keyboards.reply import get_user_kb, get_phone_button
from tgbot.misc.states import NotAuthorised, Proffer
from tgbot.services.db_base import db

user_router = Router()


@user_router.message(commands=["start"])
async def user_start(message: Message, state: FSMContext):
    user = str(message.from_user.id)
    print(user)
    check = await db.select_user(telegram_id=user)
    print(check)
    if check==None:
        await state.set_state(NotAuthorised.authorization)
        await message.answer("Приветствую! Что бы вы хотели сделать? \n",
                             reply_markup=get_user_kb())
    else:
        await message.answer("Приветствую! Что бы вы хотели сделать? \n",
                             reply_markup=get_user_kb())



@user_router.message(commands=["help"])
async def user_start(message: Message):
    await message.answer(f"Данный бот создан для проведения голосований \n"
                        f"за предложения учащихся РГУ Косыгина.\n"
                        f"Чтобы сделать предложение вам нужно авторизоваться\n"
                        f"на платформе голосований.\n")


@user_router.message(Text(text="Написать предложение"))
async def make_proffer(message: types.Message, state: FSMContext):
    await state.clear()
    user = str(message.from_user.id)
    print(user)
    check = await db.select_user(telegram_id=user)
    print(check)
    if check != None:
        await state.set_state(Proffer.title)
        await message.answer("Напишите заголовок.")
    else:
        await message.answer("Только авторизованные пользователи могут создавать\n"
                            "предложения.\nЧтобы проверить вашу авторизацию "
                            "нажмите на кнопку ниже и согласитесь на проверку по номеру телефона",
                            reply_markup=get_phone_button())


@user_router.message(Proffer.title)
async def set_content(message: Message, state: FSMContext) -> None:
    title_text = message.text
    check = False
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
                                 "что бы вы хотели предложить.")


@user_router.message(Proffer.content)
async def proffer_check(message: Message, state: FSMContext) -> None:
    check = False
    title_text = message.text
    for i in bad_words:
        if re.search(i, title_text):
            check = True
            break
    if check == True:
        await message.answer("В тексте присутсвуют нецензурные слова или символы.\n"
                             "Напишите свое предложение другими словами.")
    else:
        await state.update_data(content=message.text)



        await message.answer("Почти готово, ваше предложение будет отправлено на рассмотрение студсоветом."
                             "Как вы хотите его отправить?",
                             reply_markup=get_anon_keyboard())


@user_router.callback_query(Text(text_startswith="anon"), Proffer.content)
async def send_proffer(callback: types.CallbackQuery, state: FSMContext):
    action = callback.data.split("_")[1]
    user = callback.from_user.id
    await state.update_data(anon=action)
    data = await state.get_data()
    print(data)
    await db.add_proffer(content=data["content"], anon=bool(data["anon"]), user=user, status=1, title=data["title"])
    await callback.answer("Предложение на рассмотрении")

@user_router.message(content_types=types.ContentType.CONTACT)
async def get_contact(message: types.Message):
    contact = str(message.contact)
    check = await db.select_user(telegram_id=contact)
    print(check)
    if check != None:
        pass
    else:
        await message.answer("Вы должны авторизоваться на платформе",
                             reply_markup=get_user_kb())

