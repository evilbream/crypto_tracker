from collections.abc import Callable

from socket_request import market_registrator, request
import asyncio
from utils import default_notifications

"""
Params of the start method
notification func - any function that accepts parameters in the following format:
 param1:list = [{name: '', price: '', seller: '', pair: ''}, ...] param2: float = price gap
 as example function default_notifications is available
 
 web - True or False - to activate web interface
 tg_notification - True or False - to receive notification in Telegram, when price gap is more then gap
 database_writer - True or False - to write data in database, when price gap is more then gap
 
 gap - price gap - when price gap between currency pairs on different markets is more then the value of gap 
  - notifications in telegram and in notification function are send and the data is written to the database
  
  """

# usage example
async def main(notification_func: Callable|bool = False):
    binance = market_registrator.get('Binance')
    bybit = market_registrator.get('Bybit')
    digi = market_registrator.get('DigiFinex')
    cukoin = market_registrator.get('kuCoin')
    kraken = market_registrator.get('Kraken')
    deepcoin = market_registrator.get('Deepcoin')
    coinbase = market_registrator.get('CoinBase')
    okEx = market_registrator.get('oKex')
    await request.start([okEx, binance, bybit, digi, cukoin, kraken, deepcoin, coinbase], notification_func=notification_func,
                        tg_notifications=False, database_writer=True,
                        web=False)

if __name__ == '__main__':
    asyncio.run(main(notification_func=False))

