import requests
import websocket
import json
from socket_request.format_data import Format, Market
from socket_request.data import currency_pairs
# u can register market in any place of ur code
import re

WORD_RE = re.compile(r'[A-Z][A-Z]+')

market_registrator = Format()

@market_registrator.on('DigiFinex')
def finex_handler(name):
    val_pair = currency_pairs.copy()
    uri = 'wss://api.digifinex.com/ws/v1/'
    mes = {'id': 12312, 'method': 'trades.subscribe', 'params': val_pair}
    return Market(name, uri, mes)


@market_registrator.on('Binance') # if byer maker true then it a sell
def binance_handler(name):
    currency = currency_pairs.copy()
    currency = [''.join(pair.split('_')).lower() for pair in currency]
    uri = 'wss://stream.binance.com/stream'
    params = [f'{val}@trade' for val in currency]
    mes = {'method': 'SUBSCRIBE',  'id': 2, 'params': [*params]}
    return Market(name, uri, mes)


@market_registrator.on('Bybit')
def bybit_handler(name):
    currency = currency_pairs.copy()
    currency = [''.join(pair.split('_')).upper() for pair in currency]
    uri = 'wss://stream.bybit.com/v5/public/spot'
    params = [f'publicTrade.{val}' for val in currency]
    mes = [{'op': 'subscribe', 'args': [par]} for par in params]
    return Market(name, uri, mes)

@market_registrator.on('kuCoin')
def ku_coin(name):
    currency = currency_pairs.copy ()
    currency = [pair.replace('_', '-') for pair in currency]
    params = {"code": 200000}
    url = 'https://api.kucoin.com/api/v1/bullet-public'
    r = requests.post (url=url, data=params)
    data = json.loads(r.text)['data']
    uri = f'{data["instanceServers"][0]["endpoint"]}?token={data["token"]}'
    ws = websocket.create_connection(uri)
    res = ws.recv()
    js = json.loads(res)
    mes = {'id': js["id"], "type": "subscribe", "topic": f"/market/ticker:{','.join(currency)}",
           "response": True}
    return Market (name, uri, mes)


@market_registrator.on('Kraken')
def kraken(name):
    currency = currency_pairs.copy ()
    currency = [pair.replace ('_', '/') for pair in currency]
    uri = 'wss://ws.kraken.com'
    mes = {'event': 'subscribe', 'pair': currency, 'subscription': {'name': 'trade'}}
    return Market (name, uri, mes)

@market_registrator.on('Deepcoin')
def kraken(name):
    currency = currency_pairs.copy ()
    currency = [pair.replace ('_', '') for pair in currency]
    uri = 'wss://net-wss.deepcoin.com/public/ws'
    params = [f'DeepCoin_{cur}' for cur in currency]
    mes = [{'SendTopicAction': {'Action': '1', 'FilterValue': param, 'LocalNo': 3,
                               'ResumeNo': '-2', 'TopicID': '7'}} for param in params]
    return Market (name, uri, mes)

@market_registrator.on('CoinBase')
def coinbase(name):
    currency = currency_pairs.copy ()
    currency = [cur.replace('_', '-') for cur in currency]
    uri = 'wss://ws-feed.exchange.coinbase.com'
    mes = [{ "type": "subscribe",  "product_ids": [*currency], "channels": ['ticker']}]
    return Market(name, uri, mes)

@market_registrator.on('oKex')
def coinbase(name):
    currency = currency_pairs.copy ()
    currency = [cur.replace('_', '-') for cur in currency]
    uri = 'wss://ws.okx.com:8443/ws/v5/public'
    args = [{"channel": "tickers", "instId": pair} for pair in currency]
    mes = [{ "op": "subscribe",  "args": args}]
    return Market(name, uri, mes)





