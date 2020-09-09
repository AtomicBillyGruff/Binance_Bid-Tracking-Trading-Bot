import requests
import itertools

from binanceScratch import *
import datetime
from time import sleep

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

symbol = "ADAUSDT"
# coin_padding = .003  # based on ask / buy price
# spread_search_padding = .0002
client = Client(api_key, api_secret)

depth_cache_bid_price = []
depth_cache_bid_quantity = []
depth_cache_ask_price = []
depth_cache_ask_quantity = []

bid_dict = {}


def convert_list_toFloat(bids):  # Converting to float
    bid_temp = []
    bid_list = []
    for bid in bids:  # Float
        for elem in bid:
            elem = float(elem)
            bid_temp.append(float(elem))
        bid_list.append(list(bid_temp))
        bid_temp.clear()

    return bid_list


def process_depth(bid_list, desired_buy):  # Finding Bid CLose to Desired Buy
    coin_padding = .0015
    bid_range = []
    for bidprice in bid_list:
        if (desired_buy + coin_padding) >= bidprice[0] >= (desired_buy - coin_padding):
            bid_range.append(bidprice)

    return bid_range


def get_max_bid(bid_range, desired_buy):  # Getting Max Bidders higher than my own
    maximum = 0
    maximums_price = 0
    highest_bidders = []
    for bid in bid_range:
        if bid[1] > (desired_buy * shares * 4):
            highest_bidders.append(bid)
    # print("Highest Bidders List :", highest_bidders)
    highest_bidders.sort(key=lambda x: x[1], reverse=True)
    # print("Sorted Highest Bidders :", highest_bidders)

    return highest_bidders


def get_combinations(highest_bidders, highest_askers):  # Getting every combination of Bidder -->> Asker
    combinations = [(b, a) for b in highest_bidders for a in highest_askers]

    return combinations


def indexer(combinations, grid):  # Appending the Combinations into the Possibilities List
    possibilities = []
    for item in combinations:  # item is tuples
        possibilities.append(item)
    buy_index_counter = 0
    sell_index_counter = 1
    quick_POC = 0
    current_price = get_price()
    buyPrice = 999
    sellPrice = 999

    while quick_POC < grid and abs(current_price - buyPrice) <= .005:  # while grid condition is
        # met + spread from limit order (How quickly the trade will fire off one way)
        buyPrice = possibilities[0][buy_index_counter][0]  # gets buy price by moving index
        sellPrice = possibilities[0][sell_index_counter][0]  # gets sell price by moving index
        quick_POC = ((sellPrice - buyPrice) / buyPrice)  # percent of change
        buy_index_counter += 1
        sell_index_counter += 1
    print("BUY PRICE ", buyPrice)
    print("SELL PRICE ", sellPrice)
    print("WIN THRESHOLD ", quick_POC * 100)

    return buyPrice, sellPrice, possibilities


def Calc_Spread(desired_buy, desired_sell, fee, grid):
    res = client.get_order_book(symbol=symbol, limit=500)

    depth = {}
    bids = res["bids"]
    asks = res["asks"]
    # print(bids)
    # print(asks)

    # Convert_List_To_Float

    bid_list = convert_list_toFloat(bids)
    ask_list = convert_list_toFloat(asks)
    # print("FN ", bid_list)
    # print("FN ", ask_list)

    # print("DEBUG processing depth. . .")  # Process The Depth

    bid_range = process_depth(bid_list, desired_buy)
    ask_range = process_depth(ask_list, desired_buy)

    # print("Bids in range :", bid_range)
    # print("Asks in Range ", ask_range)

    # WIN_THRESHOLD = False
    # while not WIN_THRESHOLD:
    # print("GETTING MAX BIDDER. . .")  # Get The Max_Bidder
    highest_bidders = get_max_bid(bid_range, desired_buy)

    # buyPrice = highest_bidders + .00003
    # print("Desired Buy Price ", desired_buy)
    # print("Buy Price at ", buyPrice)

    print("GETTING MAX ASK. . .")
    highest_askers = get_max_bid(ask_range, desired_buy)

    combinations = get_combinations(highest_bidders, highest_askers)

    # print("COMBINATIONS", combinations)

    from_indexer = indexer(combinations, grid)
    buyPrice = from_indexer[0]
    sellPrice = from_indexer[1]
    possibilities = from_indexer[2]

    return buyPrice, sellPrice, possibilities, highest_askers


"----------------------------------End Of Check Bid Class-------------------------------------------------"


def begin():
    # desired_buy = float(input("Input Desired Buy Price"))
    # desired_sell = float(input("Input Desired Sell Price"))
    grid = .006
    fee = .001
    desired_buy = get_price() - .001
    desired_sell = desired_buy + (desired_buy * grid)

    desired_Percent_Of_Change = ((desired_sell - desired_buy) / desired_buy) * 100
    # Calc_Spread(desired_buy, desired_sell, fee, grid)

    print("Calculating Spread")
    tradeCount = 1
    trade = 1
    while trade <= tradeCount:
        getPrices = Calc_Spread(desired_buy, desired_sell, fee, grid)
        buyPrice = getPrices[0] - .005
        sellPrice = getPrices[1] + .005
        possibilities = getPrices[2]
        max_ask = getPrices[3]
        bought = False

        bidder(buyPrice, sellPrice, fee, desired_buy, desired_sell, bought, grid, possibilities, max_ask)

    return


def get_price():
    TICKER_API_URL = 'https://api.binance.com/api/v3/ticker/price?symbol=ADAUSDT'
    response = requests.get(TICKER_API_URL)  # can add + crypto to change crypto
    tree = str(response.content)
    CoinPrice = tree.lstrip(""" b'{"symbol":"ADAUSDT","price":" """).rstrip(""" "}' """)
    print("Price of Coin is $", CoinPrice)
    # print("ETH-USD ", tree[0].text_content()) # percents
    return float(CoinPrice)
    # (CoinPrice[1].split('-')[1])

    print("Price Fetched")


def add_closingPriceToList(Starting_Price, Current_Price, fee):
    youMadeList = []

    youMade = ((Current_Price * shares) - (Starting_Price * shares)) - (
            Starting_Price * shares * (fee * 2))
    youMadeList.append(youMade)
    print("Starting PRice; ", Starting_Price)
    print("Closing PRice; ", Current_Price)
    print("fee is: ", Starting_Price * shares * (fee * 2))
    print("You Made $", youMade)
    print("Your Trades :", youMadeList)

    tradeSum = 0

    f = open("trades.csv", "a")
    f.write("--------Trade--------- #, \n")
    now = datetime.datetime.now()
    current_time = now.strftime("%Y-%m-%d %H:%M:%S")
    for trade in youMadeList:
        f.write(str(current_time))
        f.write(',\n')
        f.write(str(trade))
        f.write(',\n')

    f.close()

    return


def calc_percent(Current_Price, Starting_Price):
    percentOfChange = (((Current_Price - Starting_Price)) / Starting_Price) * 100
    if percentOfChange > 0:
        print("[+] ", abs(percentOfChange))
    if percentOfChange < 0:
        print("[-] ", abs(percentOfChange))
    if percentOfChange == 0:
        print("[] ", percentOfChange)

    return percentOfChange


def figure_hud(Starting_Price, sellPrice, trailingPrice, stopLoss, max_ask):
    poc = 0
    Desired_Percent = 1.2
    max_ask_index = 0
    print("{DEBUG} outside figure")
    while not Desired_Percent - .5 < poc < Desired_Percent + .5:
        print("{DEBUG} inside figure")
        print("MAX_ASK", max_ask)
        try:
            sellPrice = max_ask[max_ask_index][0] - .000013
        except:
            print("no sell price Try Again")

        finally:
            print("SHOULD BE LARGEST ASKER. . .", sellPrice, max_ask[max_ask_index])

            print("Starting Price :", Starting_Price)
            print("SellPrice :", sellPrice)
            print("Trailing Price :", trailingPrice)
            print("StopLoss :", stopLoss)
            poc = ((sellPrice - Starting_Price) / Starting_Price) * 100
            print("WIN THRESHOLD : %", poc)
            max_ask_index += 1

        return sellPrice


def write_open_trades(Starting_Price):
    f = open("Trades_Open.csv", "a")
    f.write(str(Starting_Price))
    f.write(",\n")
    f.close()

    return


def write_off_sold_trades(Starting_Price):
    f = open("Trades_Open.csv", "a")
    Lines = f.readlines()
    searchquery = str(Starting_Price)
    for line in Lines:
        if line == searchquery:
            line.strip()

    f.close()

    return


class bidder(object):

    def __init__(self, buyPrice, sellPrice, fee, desired_buy, desired_sell, bought, grid, possibilities, max_ask):
        self.buyPrice = buyPrice
        self.sellPrice = sellPrice
        self.fee = fee
        self.desired_buy = desired_buy
        self.desired_sell = desired_sell
        self.bought = bought
        self.grid = grid
        self.possibilities = possibilities
        self.max_ask = max_ask
        self.limit_buy(buyPrice, sellPrice)

    def limit_buy(self, buyPrice, sellPrice):
        self.sellPrice = sellPrice
        self.buyPrice = buyPrice
        Starting_Price = 0
        possible_index = 0
        print("{DEBUG} WHILE NOT BOUGHT")
        while not self.bought:  # WHILE NOT BOUGHT
            Starting_Price = get_price()

            if buyPrice + .00016 >= Starting_Price >= buyPrice - .00016:  # IF WERE IN BALLPARK, INITIATE TRADE
                BotActivate().market_order()
                print("Price Bought At. . .", Starting_Price)
                self.bought = True
            if buyPrice + .0007 <= Starting_Price or buyPrice - .0007 >= Starting_Price:

                buyPrice = self.possibilities[0][possible_index][0]
                print("NEW POSSIBLE BUY PRICE: ", buyPrice, self.possibilities[0][possible_index])
                possible_index += 1

            else:
                sleep(2.5)
            write_open_trades(Starting_Price)
        print("{DEBUG} END OF BUY LOOP")

        self.track(Starting_Price)

    def track(self, Starting_Price):
        Current_Price = get_price()
        tradeCount = 1
        stopLoss = Starting_Price - (Starting_Price * .06)
        trailingPrice = Current_Price - stopLoss
        trailingAttack = .0003
        sold = False

        figure = figure_hud(Starting_Price, self.sellPrice, trailingPrice, stopLoss, self.max_ask)
        self.sellPrice = figure

        while not sold:  # WHILE NOT SOLD
            Current_Price = get_price()

            print("Current Price Begin of Loop", Current_Price)

            if Current_Price > Starting_Price:  # INDICATION +
                print("Going Up. . . ")

            if Current_Price < Starting_Price:  # INDICATION -
                print("Going Down. . .")

            if Current_Price == Starting_Price:  # INDICATION =
                print("Price Hasn't Moved. . .")

            if Current_Price >= self.sellPrice:  # SELLING AT SELLPRICE
                print("caught")
                BotActivate().market_sell()
                print("SOLD AT. . .", Current_Price)
                sold = True
                add_closingPriceToList(Current_Price=Current_Price, Starting_Price=Starting_Price, fee=self.fee)
                break

            if Current_Price <= Starting_Price - stopLoss:
                BotActivate().market_sell()
                print("Hit Stop Loss : SOLD AT. . .", Current_Price)
                add_closingPriceToList(Current_Price, Starting_Price, fee=self.fee)
                sold = True
                break

            perc = calc_percent(Current_Price, Starting_Price)  # GETS PERCENT OF CHANGE
            perc_deviation = .38
            if Current_Price >= trailingPrice + stopLoss and perc > perc_deviation:
                trailingPrice = Current_Price - .04
                perc_deviation *= 1.35
                print("TRAILING SET TO. . .", trailingPrice)

            if Current_Price <= trailingPrice:
                BotActivate().market_sell()
                print("SOLD AT TRAILING PRICE. . .", Current_Price)
                add_closingPriceToList(Current_Price, Starting_Price, fee=self.fee)
                sold = True
                break

            if Current_Price < self.sellPrice:
                sleep(2)
                Current_Price = get_price()
                # sellPrice = Calc_Spread(self.desired_buy, self.desired_sell, self.fee)
                # sellPrice = sellPrice[1]
                calc_percent(Current_Price, Starting_Price)

            # if perc >= .06:
            #     BotActivate().market_sell()
            #     print("SOLD AT TRAILING PERC PRICE . .", Current_Price)
            #     add_closingPriceToList(Current_Price, Starting_Price, fee=self.fee)
            #     sold = True

            sleep(4)
        write_off_sold_trades(Starting_Price)

        return


# desired_buy = .04935
# desired_sell = .4955
# fee = .001
# stuff = Calc_Spread(desired_buy, desired_sell, fee)
# print("Calc_Spread : ", stuff)


class newYuKungFu(object):

    def __init__(self, fee):
        self.fee = fee

        # Starting_Price = float(input("Starting PRice"))
        # Sell_Price = float(input("Desired SEll PRice"))

        desired_buy = .05
        desired_sell = .05
        #
        # q_poc = ((Sell_Price - Starting_Price)/Starting_Price)
        # print("[] WIN THRESHOLD : %", q_poc * 100)

        print("These are the options in range of you bid. . .")

        res = client.get_order_book(symbol=symbol, limit=500)

        bids = res["bids"]
        asks = res["asks"]

        bidList = convert_list_toFloat(bids)
        askList = convert_list_toFloat(asks)

        bidProcess = process_depth(bidList, desired_buy)
        askProcess = process_depth(askList, desired_sell)

        Max_Bidder = get_max_bid(bidProcess, desired_buy)
        self.Max_Asker = get_max_bid(askProcess, desired_sell)

        print("MAX BIDDERS ", Max_Bidder)
        print("MAX ASKER ", self.Max_Asker)

        Succeeded = False
        while not Succeeded:

            for bid in Max_Bidder:
                checkBid = self.newFunction(bid, Succeeded)
                Starting_Price = checkBid[0]
                Succeeded = checkBid[1]
                if Succeeded == True:
                    break
                break

        self.track(Starting_Price)

        return

    def newFunction(self, bid, Succeeded):
        self.bid = bid
        self.Succeeded = Succeeded

        print("Seeing if this works")
        current_price = get_price()
        quick_poc = abs(((current_price - self.bid[0]) / self.bid[0]) * 100)
        if quick_poc > .07:
            BotActivate().market_order()
            print("Market Order Placed at. . .", current_price)
            self.Succeeded = True

        else:
            print("Quick Poc not spread enough")

        return current_price, self.Succeeded

    def track(self, Starting_Price):
        Current_Price = get_price()
        tradeCount = 1
        stopLoss = Starting_Price - (Starting_Price * .06)
        trailingPrice = Current_Price - stopLoss
        trailingAttack = .0003
        sold = False
        sellPrice = Current_Price + (Current_Price * .005)

        figure = figure_hud(Starting_Price, sellPrice, trailingPrice, stopLoss, self.Max_Asker )
        sellPrice = figure

        while not sold:  # WHILE NOT SOLD
            Current_Price = get_price()

            print("Current Price Begin of Loop", Current_Price)

            if Current_Price > Starting_Price:  # INDICATION +
                print("Going Up. . . ")

            if Current_Price < Starting_Price:  # INDICATION -
                print("Going Down. . .")

            if Current_Price == Starting_Price:  # INDICATION =
                print("Price Hasn't Moved. . .")

            if Current_Price >= sellPrice:  # SELLING AT SELLPRICE
                print("caught")
                BotActivate().market_sell()
                print("SOLD AT. . .", Current_Price)
                sold = True
                add_closingPriceToList(Current_Price=Current_Price, Starting_Price=Starting_Price, fee=self.fee)
                break

            if Current_Price <= Starting_Price - stopLoss:
                BotActivate().market_sell()
                print("Hit Stop Loss : SOLD AT. . .", Current_Price)
                add_closingPriceToList(Current_Price, Starting_Price, fee=self.fee)
                sold = True
                break

            perc = calc_percent(Current_Price, Starting_Price)  # GETS PERCENT OF CHANGE
            perc_deviation = .38
            if Current_Price >= trailingPrice + stopLoss and perc > perc_deviation:
                trailingPrice = Current_Price - .04
                perc_deviation *= 1.35
                print("TRAILING SET TO. . .", trailingPrice)

            if Current_Price <= trailingPrice:
                BotActivate().market_sell()
                print("SOLD AT TRAILING PRICE. . .", Current_Price)
                add_closingPriceToList(Current_Price, Starting_Price, fee=self.fee)
                sold = True
                break

            if Current_Price < sellPrice:
                sleep(2)
                Current_Price = get_price()
                # sellPrice = Calc_Spread(self.desired_buy, self.desired_sell, self.fee)
                # sellPrice = sellPrice[1]
                calc_percent(Current_Price, Starting_Price)

            # if perc >= .06:
            #     BotActivate().market_sell()
            #     print("SOLD AT TRAILING PERC PRICE . .", Current_Price)
            #     add_closingPriceToList(Current_Price, Starting_Price, fee=self.fee)
            #     sold = True

            sleep(4)
        write_off_sold_trades(Starting_Price)

        return
fee = .001
max_ask  = 0
newYuKungFu(fee)
