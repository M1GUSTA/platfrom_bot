from aiogram import Bot
from aiogram.methods import SendMessage
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from tgbot.config import Config
from tgbot.keyboards.inline import get_check_keyboard
from tgbot.services.db_base import db
from datetime import datetime, timedelta



async def check_spam():
    proffers = await db.get_all_proffers(id_status=6)
    for proffer in proffers:
        cur_date = datetime.now().date()
        if (cur_date-timedelta(days=14))==proffer["date_act"]:
            try:
                print(proffer["id_proffer"])
                await db.delete_proffer(id_proffer=proffer["id_proffer"])
            except Exception as ex:
                print(ex)


async def check_site_proffs(config: Config, bot: Bot):
    proffers = await db.get_all_proffers(id_status=1)
    print('проверка')
    print(proffers)
    for proffer in proffers:
        for admin in config.tg_bot.admin_ids:
            print(admin)
            # if bool(data["anon"])==True:
            await bot.send_message(chat_id=admin, text=f"Пришло новое предложение!\n\n\n"
                                                  f"{proffer['title']}\n\n"
                                                  f"{proffer['content']}",
                              reply_markup=get_check_keyboard())
