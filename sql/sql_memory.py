import json

import websockets

from socket_request.format_data import market_registrator
from sql.core import Trade, Base
import asyncio
import datetime
from typing import List

from sqlalchemy import ForeignKey
from sqlalchemy import func
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy.orm import selectinload


async def insert_objects(async_session, market, price, seller, currency_pair):
    async with async_session() as session:
        async with session.begin():
            session.add_all([
                Currency_pairs(trade=[Trade(market=market,
                                                 price=price,
                                                 seller=seller),], currency_pair=currency_pair),]
            )




async def async_main() -> None:
    engine = create_async_engine(
        "sqlite+aiosqlite:///crypto_markets.db",
        echo=True,
    )

    # async_sessionmaker: a factory for new AsyncSession objects.
    # expire_on_commit - don't expire objects after transaction commit
    async_session = async_sessionmaker(engine, expire_on_commit=False)
    async with engine.begin () as conn:
        await conn.run_sync (Base.metadata.create_all)

    for market, price, seller, currency_pair in data:
        await insert_objects (async_session, market, price, seller, currency_pair)

    # for AsyncEngine created in function scope, close and
    # clean-up pooled connections
    await engine.dispose()

uri = market_registrator.get('Binance')
print(uri)


async def connect_to_server():
    async for ws in  websockets.connect(uri.uri):
        await ws.send(uri.command)
        while True:
            res = await ws.recv()
            print(json.loads(res))
            """try:
                if js['stream'].endswith('@bookTicker'):
                    pass
                    #print(f"Pair: {js['data']['s']}\nBest Sell: {js['data']['a']}\nBest Buy: {js['data']['b']}\nTime:{datetime.now()}\n")
                elif js['stream'].endswith('trade'):
                    print(f"Pair: {js['data']['s']}\nPrice: {js['data']['p']}\nTime:{datetime.now()}\n")
            except KeyError:
                continue"""

asyncio.run(connect_to_server())
#asyncio.run(async_main())
