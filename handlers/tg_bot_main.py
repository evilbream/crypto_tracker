from utils import TG_TOKEN
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from handlers.tg_handlers import router


async def bot_tg():
    dp = Dispatcher ()
    dp.include_routers (router)
    bot = Bot (TG_TOKEN, parse_mode=ParseMode.HTML)
    await dp.start_polling (bot, skip_updates=True)