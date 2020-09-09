from binance.client import Client
from binance.websockets import BinanceSocketManager
import pandas as pd
import pandas_datareader as web
from apiKey import api_secret, api_key
import datetime
import yfinance as yf
import matplotlib as mpl

from pandas.util.testing import assert_frame_equal

client = Client(api_key, api_secret)

Coin_Amt = .5
class DefineTicker:

    def get_ticker_data(self):
        tickerSymbol = 'ETH-USD'
        tickerData = yf.Ticker(tickerSymbol)
        tickerDf = tickerData.history(period='1d', start='2020-3-23', end='2020-4-23')
        print(tickerDf)

class BotActivate:

    def market_order(self):
        print('it works ')
        print('[+] Placing test market buy order')
        order = client.create_test_order(
            symbol='ETHUSDT',
            side=Client.SIDE_BUY,
            type=Client.ORDER_TYPE_MARKET,
            quantity=Coin_Amt

        )
        print('real order placed')

    def market_sell(self):
        print('Selling ... .  ')
        print('[+] preparing to sell at desired limit')
        order = client.create_test_order(
            symbol='ETHUSDT',
            side=Client.SIDE_SELL,
            type=Client.ORDER_TYPE_MARKET,
            quantity=Coin_Amt

        )
        print('Order Sold...')


# activate bot
# xrange = BotActivate().test_market_order()
# print(xrange)
url = 'https://api.binance.com/api/v1/ticker/24hr'

# class GraphDataFrom:
#
#
#     read = web.DataReader('ETH-USD', data_source='yahoo', start='4/14/2020',
#                           end='4/15/2020')
#     # print(read)
#     print("<------Choices-------------------------->")
#     # for col in read.columns:
#     #     print(col)
#     print(read)
#     # print(read.iloc[:1, :1])
#
#     #
#     # plt = mpl.pyplot
#     # print(plt)


'--------------user--------------'
# getting_data = DefineTicker().get_ticker_data()