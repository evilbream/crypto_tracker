import random

from aiogram.exceptions import TelegramRetryAfter
from aiogram.filters import Command
import asyncio
from aiogram import Router, types
from utils.storage import cross_storage

router = Router()

@router.message (Command ("start"))
async def start_handler(mes: types.Message):
    gap = 12
    await mes.answer('Starting to check prices on markets')
    while True:
        try:
            lis = cross_storage.pick(cross_storage.TELEGRAM) # format: [[{name, price, seller, pair}, ...], price_gap]
            if lis:
                new_gap = lis[1]
                if int(gap) <= int(new_gap) <= int(gap):
                    continue
                markets = [f'{i["name"]}: {round(float(i["price"]), 2)}' for i in lis[0]]
                pair = [f'{(i["pair"])}' for i in lis[0]][0]
                answ = f'Gap: {lis[1]}. Pair - {pair}\n' \
                           f'{" | ".join (markets)}'
                gap = lis[1]
                await mes.answer(answ)
                await asyncio.sleep(random.uniform(0.05, 0.2))
            else:
                await asyncio.sleep(1)
        except TelegramRetryAfter:
            await asyncio.sleep(2)
            continue