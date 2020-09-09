from binance.client import Client
from binance.websockets import BinanceSocketManager
from binanceScratch import client
shares = .6


def market_sell():
    print('it works ')
    print('[+] Placing market sell order')

    order = client.create_test_order(
        symbol='ETHUSDT',
        side=Client.SIDE_SELL,
        type=Client.ORDER_TYPE_MARKET,
        quantity=shares

    )
    print('real order placed')

    "order attempted"

market_sell()
print("Tracking to Sell")
starting_price = input("Input Starting Price")

