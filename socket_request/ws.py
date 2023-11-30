import asyncio
import json
import random
import sys
import time

import websockets
from typing import Callable
from dataclasses import dataclass

from handlers import bot_tg
from socket_request.data import PRICE_GAP, currency_pairs
from socket_request.register_markets import market_registrator, Market

from sql.management import start_db, write_to_database
from utils.storage import cross_storage
from threading import Lock

from web_interface.web_snout_2 import run_web


class Trade_online:
    def __init__(self, val):
        self.market_list:list = []
        self.val: str = val

    def add(self, trade_dict: dict) -> dict[list]:
        if trade_dict not in self.market_list:
            if self.market_list and (trade_dict['name'] in [old_dict['name'] for old_dict in self.market_list]):

                name_to_remove = [old_dict for old_dict in self.market_list if (old_dict['name'] == trade_dict['name'])]
                self.market_list.remove(name_to_remove[0])
                self.market_list.append(trade_dict)
            else:
                self.market_list.append(trade_dict)
        return {self.val.replace('_', ''): self.market_list}

    def __repr__(self):
        if self.market_list:
            try:
                markets = [f'{i["name"]:<20}' for i in self.market_list]
                price = [f'{i["price"]:<20}' for i in self.market_list]
                return f'\n{self.val}\n' \
                       f'{" | ".join(markets)}\n' \
                       f'{" | ".join (price)}\n'
            except IndexError:
                return f'Current price: {self.market_list}'
        else:
            return ''



class Price_notifications:
    def __init__(self, gap, notify_func: Callable):
        self.notify_func = notify_func
        self.gap = gap

    @staticmethod
    def gap_finder(prices: set[float]) -> float:
        if len (prices) == 0:
            return 0
        return round (max (prices) - min(prices), 4)

    def notify_about_gap(self, market_dict: dict, storage=False, web=False, telegram=False):
        markets = [v for k, v in market_dict.items ()][0]
        prices = {float (market['price']) for market in markets}
        real_gap = self.gap_finder (prices)
        #print (f'Gap: {real_gap}')
        #print (markets) #prints market data in the following format [{name, price, seller, pair}, ...]
        if web:
            # with Lock(): lock used only if server in thread mode
            cross_storage[cross_storage.WEB] = [markets, real_gap]
        if real_gap >= self.gap:
            if self.notify_func is not None:
                self.notify_func(markets, real_gap)
            #gap_list.appendleft((markets, real_gap))
            if storage:
                asyncio.create_task(write_to_database((markets, real_gap), storage))
            if telegram:
                cross_storage[cross_storage.TELEGRAM] = (markets, real_gap)
            # return func(self.market_list)
            # add trade data


value_dict = {}
for val in currency_pairs:
    value_dict["".join(val.split("_"))] = Trade_online(val)


@dataclass
class Request:
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
    handlers = dict ()
    price_gap: float = PRICE_GAP
    notification_func: Callable = None
    database_writer: Callable=None # функция для записи в датабазу. ей передается словарь после каждого добавления значения
    storage = False
    web = False
    telegram = False

    def add(self, command):
        def deco(func):
            if command not in self.handlers.keys ():
                self.handlers[command] = func
            return func

        return deco

    def weight_price(self, **kwargs):
        global trade_lock
        pair = kwargs['pair']
        market_list = value_dict[pair].add(kwargs)
                #create_table(vd)
        self.notify.notify_about_gap(market_list, self.storage, self.web, self.telegram)
                # call notification function ad to lock if errors occured
    def handle(self, market, result):
        if market in self.handlers.keys ():
            kwargs = self.handlers[market] (result)
            self.weight_price(**kwargs) if kwargs is not None else '' # do something with results add to db etc
        else:
            print (f'Unexpected market. Data: {market}.')
            print (result)

    @staticmethod
    def time_checker(timer: int, start):
        now = time.time ()
        return True if now - start > timer else False

    async def _run(self, market: Market):
        start = time.time()
        async for ws in websockets.connect(market.uri, user_agent_header=self.user_agent):
            try:
                for i in market.command:
                    await ws.send(i)
                while True:
                    if self.time_checker(1000, start): #send pong
                        start = time.time ()
                        await ws.ping() if random.randint(0, 1) == 1 else await ws.pong()
                    res = await ws.recv()
                    self.handle(market.name, res)

            except websockets.ConnectionClosed:
                market = market_registrator.get (market.name) # when disconnected request again market object
                continue

    async def start(self, markets: list[Market], gap:int|float=False, notification_func: Callable=False,
                    database_writer=False, tg_notifications=False, web=False):
        if notification_func:
            self.notification_func = notification_func
        if database_writer:
            self.storage = await start_db()
        if gap:
            self.price_gap = gap
        self.notify: Price_notifications = Price_notifications (self.price_gap, self.notification_func)
        try:
            if web: # do all the things with the web
                self.web = True
                cross_storage[cross_storage.MARKET] = [market.name for market in markets]
                await asyncio.gather (*[*[self._run (market) for market in markets], run_web()]) #run markets + web interface
            if tg_notifications: # do all things with the telegram
                asyncio.create_task(bot_tg())
                self.telegram = True
            if not web:
                await asyncio.gather(*[self._run(market) for market in markets]) # run markets only
        except KeyboardInterrupt:
            print('Exiting')
            sys.exit(0)



if __name__ == '__main__':
    pass



