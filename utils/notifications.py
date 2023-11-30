

def default_notifications(message: list, gap):
    pair = [i["pair"] for i in message][0]
    print(f'Max price gap on {pair}: {gap}')
    markets = [f'{i["name"]:<20}' for i in message]
    price = [f'{i["price"]:<20}' for i in message]
    print(f'{" | ".join (markets)}\n{" | ".join (price)}\n')
