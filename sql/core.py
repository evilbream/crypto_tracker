import asyncio
import datetime
from pathlib import Path
from typing import Optional, List

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import Session, MappedAsDataclass, selectinload
import sqlalchemy
from sqlalchemy import select, func
from sqlalchemy import create_engine
from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship



class Base(DeclarativeBase):
    pass


class Currency(Base):
    __tablename__ = 'Currency'
    id: Mapped[int] = mapped_column (primary_key=True)
    name: Mapped[str] = mapped_column ()

    def __repr__(self):
        return f'Currency(id={self.id}, name={self.name})'


class Market (Base):
    __tablename__ = "Market"
    id: Mapped[int] = mapped_column (primary_key=True)
    name: Mapped[str] = mapped_column ()

    def __repr__(self):
        return f'Market(id={self.id}, name={self.name})'


class Trade_data(Base):
    __tablename__ = 'Trade_data'
    id: Mapped[int] = mapped_column (primary_key=True)
    currency_id: Mapped[str] = mapped_column(ForeignKey('Currency.id'))
    market_id: Mapped[str] = mapped_column(ForeignKey('Market.id'))
    trade: Mapped[list["Trade"]] = relationship(back_populates='trade_data',  cascade="all, delete-orphan")

    def __repr__(self):
        return f'Trade_data(id={self.id}, currency_id={self.currency_id}, market_id={self.market_id}, trade={self.trade})'

class Trade(Base):
    __tablename__ = 'Trade'
    transaction_id: Mapped[int] = mapped_column(primary_key=True)
    mark_cur_id: Mapped[int] = mapped_column (ForeignKey('Trade_data.id'))
    price: Mapped[float]
    seller: Mapped[bool]
    gap: Mapped[float]
    date: Mapped[datetime.datetime] = mapped_column(server_default=func.now())
    trade_data: Mapped["Trade_data"] = relationship(back_populates='trade')

    def __repr__(self):
        return f'Trade(transaction_id={self.transaction_id}, mark_cur_id={self.mark_cur_id}, seller={self.seller},' \
               f'date={self.date})'


engine = create_engine('sqlite:///test.db', echo=True)
#Base.metadata.create_all(engine)


dicts = {'BTCUSD': [{'name': 'Kraken', 'price': '36995.00000', 'seller': True, 'pair': 'BTCUSD'}]}

class SQL_storage:
    def __init__(self, db_name=None):
        if db_name:
            self._engine = create_async_engine (db_name, echo=True)
        else:
            self._engine = create_async_engine (f'sqlite+aiosqlite:///{Path(__file__).parent}\\test.db', echo=True)

    async def create_tables(self):
        async with self._engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    def _session(self):
        return async_sessionmaker(self._engine, expire_on_commit=False)

    async def _select(self, statement):
        async with self._session()() as session:
            res = await session.execute(statement)
            return res

    async def fetch_one(self, statement):
        result = await self._select(statement)
        return result.scalar()

    async def fetch_all(self, statement):
        result = await self._select(statement)
        return result.scalars()

    async def add_one(self, added_object, condition_stmt, without_condition=False):
        async with self._session()() as session:
            async with session.begin():
                if without_condition:
                    session.add (added_object)
                else:
                    condition = await self.fetch_one(condition_stmt)
                    if condition is None:
                        session.add(added_object)

    async def add_multiple(self, added_objects):
        async with self._session()() as session:
            async with session.begin ():
                session.add_all(added_objects)

    async def add_trade_data(self, currency, market, price, seller, gap):
        trade_data = await self.fetch_one(select (Trade_data.id).join (Currency).join (Market).where (Currency.name == currency).where (Market.name == market))
        if trade_data is None:
            cur_id = await self.fetch_one (select (Currency.id).where (Currency.name == currency))
            market_id = await self.fetch_one (select (Market.id).where (Market.name == market))
            stmt = Trade_data (currency_id=cur_id, market_id=market_id,
                                     trade=[Trade (price=price, seller=seller, gap=gap),])
            await self.add_one(stmt, None, without_condition=True)
        else:
            await self.add_one(Trade (mark_cur_id=trade_data, price=price, seller=seller, gap=gap), None, without_condition=True)




currency_pairs = ['BTC_USDT', 'ETH_USDT', 'BTC_USD']
markets = ['Binance', 'Bybit', 'kuCoin', 'Kraken', 'Deepcoin', 'DigiFinex']

data = [{'name': 'kuCoin', 'price': '36330.4', 'seller': False, 'pair': 'ETH_USDT'}, {'name': 'Binance', 'price': '36329.17000000', 'seller': True, 'pair': 'ETH_USDT'}, {'name': 'Deepcoin', 'price': '36337.1', 'seller': False, 'pair': 'BTC_USDT'}, {'name': 'DigiFinex', 'price': '36329.41', 'seller': True, 'pair': 'BTC_USDT'}]

async def main():
    storage = SQL_storage()
    """await storage.create_tables()
    # add markets and currency pairs
    [await storage.add_one(Currency(name=cur.replace('_', '')), select(Currency).where(Currency.name==cur.replace('_', ''))) for cur in currency_pairs]
    [await storage.add_one (Market (name=cur), select (Market).where (Market.name == cur)) for cur in
     markets]
"""
    #for pair in data:
        #await storage.add_trade_data((pair['pair']).replace('_', ''), pair['name'], pair['price'], pair['seller'], 12)
    # examples of fetching results
    currency_id = await storage.fetch_one(select(Currency.id).where(Currency.name=='BTCUSDT'))

    res = await storage.fetch_all(select (Trade_data.id).join(Currency).where(Currency.name=='BTCUSDT'))
    mark = [*res]
    res = await storage.fetch_all(select (Trade).join(Trade_data).where(Trade_data.id.in_(mark)).order_by(Trade.gap))
    gap = (max([i.gap for i in res]))
    res = await storage.fetch_all (select (Trade).where (Trade.gap==gap))
    for i in res:
        print(i.date, i)
#asyncio.run(main())

















def create_table(market_dict: dict):
    global i
    global transaction_id
    with Session(engine) as session:
        market_table = [Market(id=j, name=mark) for j, mark in enumerate(markets)]
        cur_table = [Currency(id=j, name=cur.replace('_', '')) for j, cur in enumerate(currency_pairs)]
        for k, v in market_dict.items():
            if v:
                print(v, 'ffff')
                market_name = market_dict[k][0]['name']
                price = float(market_dict[k][0]['price'].rstrip('0'))
                cur = select(Currency).where(Currency.name.in_([k]))
                cur_id = session.scalar(cur).id

                mark = select (Market).where (Market.name.in_ ([market_name]))
                mark_id = session.scalar (mark).id

                stm = select(Trade_data).join(Currency).join(Market).where(Currency.name==k).where(Market.name==market_name)
                if session.scalar(stm) is None:
                    trade_data = Trade_data (id=i, currency_id=cur_id, market_id=mark_id,
                                             trade=[Trade (transaction_id=transaction_id, price=price, seller=True)])
                    with Session (engine) as session:
                        session.add (trade_data)
                        session.commit ()
                        i += 1
                        transaction_id+= 1
                else:
                    with Session (engine) as ses:
                        stm = select (Trade_data).join (Currency).join (Market).where (Currency.name == k).where (
                            Market.name == market_name)
                        cur_trade = ses.scalar (stm)
                        transaction_id += 1
                        cur_trade.trade.append (Trade (transaction_id=transaction_id, price=price, seller=True))
                        ses.commit ()
                        print (cur_trade)



def delete_some():
    with Session(engine) as ses:
        stm = select (Trade)
        for i in ses.scalars(stm):
            ses.delete(i)
        ses.commit()








