from socket_request.ws import Request
import json
import zlib

request = Request()

@request.add('Binance')
def binance(res) -> dict|None:
    js = json.loads(res)
    if js.get('stream', '1').endswith ('trade'):  # market, price, seller, currency_pair
        seller = True if js['data']['m'] is True else False
        return {'name': 'Binance', 'price': js['data']['p'], 'seller': seller, 'pair': js['data']['s']}
    return None
@request.add('Bybit')
def binance(res) -> dict|None:
    js = json.loads(res)
    if js.get('topic', '1').startswith('publicTrade.'):
        for trade in js['data']:
            seller = True if trade['S'] == 'Sell' else False
            return {'name': 'Bybit', 'price': trade['p'], 'seller': seller, 'pair': trade['s']}
    elif js.get('success', '1') is False:
        print(f'Unable to subscribe to this pair {js.get("ret_msg", "1")}')
        return None

@request.add('DigiFinex')
def digi(res) -> dict|None:
    decomp = zlib.decompress (res)
    js = json.loads(decomp)
    if js.get('method', '1').startswith('trades.update'):
        pair = ''.join(js['params'][2].split('_'))
        for trade in js['params'][1]:
            seller = True if trade['type'] == 'sell' else False
            return {'name': 'DigiFinex', 'price': trade['price'], 'seller': seller, 'pair': pair}
    return None
@request.add('kuCoin')
def digi(res) -> dict|None:
    js = json.loads(res)
    if js.get('topic', '1').startswith('/market/ticker'):
        pair = js['topic'].lstrip('/market/ticker:').replace('-', '') # replace with re
        seller = False
        return {'name': 'kuCoin', 'price': js['data']['price'], 'seller': seller, 'pair': pair}
    return None
@request.add('Kraken')
def kraken(res) -> dict|None:
    js = json.loads (res)
    #print(js)
    try:
        if 'trade' in js:
            if 'XBT' in js[-1]:
                pair = js[-1].replace ('XBT', 'BTC').replace('/', '')
            else:
                pair = js[-1].replace ('/', '') # replace with re
            seller = True if js[1][0][3] == 's' else False
            #print({'name': 'Kraken', 'price': js[1][0][0], 'seller': seller, 'pair': pair})
            return {'name': 'Kraken', 'price': js[1][0][0], 'seller': seller, 'pair': pair}
    except IndexError or TypeError or KeyError:
        return None

@request.add('Deepcoin')
def kraken(res) -> dict|None:
    js = json.loads (res)
    if js.get('result', '1') != '1':
        try:
            price = js['result'][0]['data']['LastPrice']
            pair = js['result'][0]['data']['InstrumentID']
            return {'name': 'Deepcoin', 'price': str(price), 'seller': False, 'pair': pair}
        except KeyError:
            return None

@request.add('CoinBase')
def coinbase(res) -> dict|None:
    js = json.loads (res)
    if js.get('type', '1') != '1':
        try:
            pair = js['product_id'].replace('-', '')
            seller = False if js['side'] == 'buy' else True
            return {'name': 'CoinBase', 'price': js['price'], 'seller': seller, 'pair': pair}
        except KeyError:
            return None
    return None

@request.add('oKex')
def coinbase(res) -> dict|None:
    js = json.loads (res)
    #print(js)
    if (js.get('arg', '1') != '1') and (js['arg'].get('channel', '1') == 'tickers'):
        try:
            pair = js['arg']['instId'].replace('-', '')
            price = js['data'][0]['last']
            seller = False
            return {'name': 'oKex', 'price': price, 'seller': seller, 'pair': pair}
        except KeyError:
            return None
    elif js.get('event', '1') == 'error':
        print('oKex', js.get('msg', '1'))
    return None


