from binance.client import Client
from binance.websockets import BinanceSocketManager
from binanceScratch import client

shares = 5


def market_order():
    print('it works ')
    print('[+] Placing test market buy order')
    try:
        order = client.create_order(
            symbol='NULSUSDT',
            side=Client.SIDE_BUY,
            type=Client.ORDER_TYPE_MARKET,
            quantity=shares

        )
        print('real order placed')
    finally:
        "order attempted"

market_order()

