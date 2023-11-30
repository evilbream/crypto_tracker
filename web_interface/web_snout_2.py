import json
from functools import partial
#from socket_request.data import markets
from utils.storage import cross_storage
import asyncio
import websockets


def unify_data(datas): # расположить данные так как они расположены в таблице
    markets = cross_storage[cross_storage.MARKET]
    ranged_markets = ['-' for _ in range(len(markets) + 2)]
    ranged_markets[0] = datas[0][0]['pair']
    ranged_markets[-1] = datas[-1]
    for i in datas[0]:
        ranged_markets[markets.index(i['name']) + 1] = round(float(i['price']), 4)
    return ranged_markets


async def handler(websocket, time_interval, notify_gap):
    markets = cross_storage[cross_storage.MARKET]
    # {name: market, markets: [market, ...]}
    try:
        await websocket.send (json.dumps ({'name': 'market', 'markets': markets, 'notify_gap': notify_gap}))
    except websockets.ConnectionClosedOK:
        print (f'Client closed connection')
        return

    while True:
        data = cross_storage.pick(cross_storage.WEB)
        #print(data)
        if data:
            data = {'name': 'pair', 'pair': unify_data (data)}
            #print(data)
            try:
                await websocket.send(json.dumps(data))
            except websockets.ConnectionClosedOK:
                print(f'Client closed connection')
                break
            await asyncio.sleep(time_interval)
        else:
            await asyncio.sleep(1)


async def run_web(time_interval=0.2, notify_gap=2):
    async with websockets.serve(partial(handler, time_interval=time_interval, notify_gap=notify_gap), '', 8001):
        await asyncio.Future()