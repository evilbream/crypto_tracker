import asyncio
from collections import deque

from socket_request.data import currency_pairs, markets
from sql.core import SQL_storage, Currency, Market
from sqlalchemy import select


class Remember:
    def __init__(self):
        self.memory = {}

    def __call__(self, pair, new_value):
        try:
            if self.memory[pair] == new_value:
                return True
            self.memory[pair] = new_value
            return False
        except KeyError:
            self.memory[pair] = new_value
            return False


async def start_db():
    storage = SQL_storage ()
    await storage.create_tables ()
    # add markets and currency pairs
    [await storage.add_one (Currency (name=cur.replace ('_', '')),
                            select (Currency).where (Currency.name == cur.replace ('_', ''))) for cur in currency_pairs]
    [await storage.add_one (Market (name=cur), select (Market).where (Market.name == cur)) for cur in
     markets]
    return storage

remember = Remember()
async def write_to_database(data, storage):
    if remember (data[0][0]['pair'], data[1]) is False:
            for pair in data[0]:
                await storage.add_trade_data((pair['pair']).replace('_', ''), pair['name'], pair['price'], pair['seller'], data[1])
