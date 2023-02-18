import asyncio
import logging


from aiogram import Bot, Dispatcher
from aiogram.dispatcher.fsm.storage.memory import MemoryStorage
# import aioschedule
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from tgbot.config import load_config
from tgbot.handlers.admin import admin_router
from tgbot.handlers.echo import echo_router
from tgbot.handlers.user import user_router
from tgbot.middlewares.config import ConfigMiddleware
from tgbot.middlewares.throttling import ThrottlingMiddleware

from tgbot.services import broadcaster
from tgbot.services.db_base import db
from tgbot.services.schedulesJobs import check_spam, check_site_proffs

logger = logging.getLogger(__name__)

def schedule_jobs(scheduler, config, bot):
    scheduler.add_job(check_spam, 'interval', hours=24)
    scheduler.add_job(check_site_proffs, 'interval', seconds=30, args=(config, bot))


async def on_startup(bot: Bot, admin_ids: list[int], db):
    logging.info("Создаем подключение к базе данных")
    await db.create()
    await broadcaster.broadcast(bot, admin_ids, "Бот запущен!")



def register_global_middlewares(dp: Dispatcher, config):
    dp.message.outer_middleware(ConfigMiddleware(config))
    dp.callback_query.outer_middleware(ConfigMiddleware(config))
    dp.message.middleware(ThrottlingMiddleware())


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format=u'%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s',
    )
    logger.info("Starting bot")
    config = load_config(".env")

    storage = MemoryStorage()
    bot = Bot(token=config.tg_bot.token, parse_mode='HTML')
    dp = Dispatcher(storage=storage)

    scheduler = AsyncIOScheduler()


    for router in [
        user_router,
        admin_router,
        echo_router
    ]:
        dp.include_router(router)


    schedule_jobs(scheduler, config, bot)


    register_global_middlewares(dp, config)
    await on_startup(bot, config.tg_bot.admin_ids, db)
    try:
        scheduler.start()
        await dp.start_polling(bot)
    finally:
        await dp.storage.close()
        await db.storage.wait_closed()
        await bot.session.close()




if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.error("Бот остановлен!")
