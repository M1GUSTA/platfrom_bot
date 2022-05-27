from aiogram import types, Router, F
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.utils.markdown import hcode

echo_router = Router()


@echo_router.message(F.text, state=None)
async def bot_echo(message: types.Message):
    text = [
        "Ехо без состояния.",
        "Сообщение:",
        message.text
    ]

    await message.answer('\n'.join(text))


@echo_router.message(F.text)
async def bot_echo_all(message: types.Message, state: FSMContext):
    state_name = await state.get_state()
    text = [
        f'Ехо с состоянием {hcode(state_name)}',
        'Сообщение:',
        hcode(message.text)
    ]
    await message.answer('\n'.join(text))

