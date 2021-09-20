import pandas as pd
import yfinance as yf
import datetime, time
# TODO: fix the change column in Account.df


class Account:
    def __init__(self):
        self.name = ""
        self.cash = 0
        self.valuation = 0
        self.asset = []
        self.df = pd.DataFrame()

    def getValuation(self):
        value = self.cash
        for stock in self.asset:
            if stock.type == "Long":
                stock.value = stock.sellValue()
            else:
                stock.value = stock.buyValue()
            value += stock.value * stock.shares
        return value


class Asset:
    def __init__(self):
        self.ticker = None
        self.value = 0
        self.type = "Long"
        self.shares = 1

    def newValue(self):
        return self.getValue(self.ticker, 0)

    def buyValue(self):
        return self.getValue(self.ticker, 1)

    def sellValue(self):
        return self.getValue(self.ticker, 2)

    @staticmethod
    def getValue(ticker, cmd):
        if ticker is None:
            value = 0
        else:
            if cmd == 0:
                value = yf.Ticker(ticker).info['currentPrice']
            elif cmd == 1:
                value = yf.Ticker(ticker).info['ask']
            elif cmd == 2:
                value = yf.Ticker(ticker).info['bid']

        return value


def bto_asset(acct, tick, shares):
    stock = Asset()
    tick = tick.upper()
    stock.ticker = str(tick)
    stock.value = stock.buyValue()
    stock.shares = int(shares)
    acct.asset.append(stock)
    acct.cash -= stock.value * shares
    update_acct(acct)


def stc_asset(acct, tick, shares):
    for x in acct.asset:
        if x.ticker == tick and x.type == "Long":
            if x.shares - shares >= 0:
                x.value = x.sellValue()
                acct.cash += x.value * shares
                x.shares -= shares
                if x.shares == 0:
                    acct.asset.remove(x)
                update_acct(acct)
            else:
                print("You don't have that many shares")


def sto_asset(acct, tick, shares):
    stock = Asset()
    stock.ticker = tick
    stock.value = stock.sellValue()
    stock.shares = -shares
    stock.type = "Short"
    acct.asset.append(stock)
    acct.cash += stock.value * shares
    update_acct(acct)


def btc_asset(acct, tick, shares):
    for x in acct.asset:
        if x.ticker == tick and x.type == "Short":
            if x.shares - shares <= 0:
                x.value = x.buyValue()
                acct.cash -= x.value * shares
                x.shares += shares
                if x.shares == 0:
                    acct.asset.remove(x)
                update_acct(acct)
            else:
                print("You don't have that many shares")


def create_acct(name, cash):
    acct = Account()
    acct.name = str(name)
    acct.cash = float(cash)
    data_dict = {'Date-Time': datetime.datetime.now(),
                 'Name': [str(acct.name)],
                 'Cash': [float(acct.cash)],
                 'value': [acct.getValuation()],
                 'Change': [0]}

    acct.df = pd.DataFrame(data=data_dict)
    return acct


def update_acct(acct):
    acct.valuation = acct.getValuation()
    data_dict = {'Date-Time': datetime.datetime.now(),
                 'Name': [str(acct.name)],
                 'Cash': [float(acct.cash)],
                 'value': [acct.getValuation()],
                 'Change': [0]}
    df = pd.DataFrame(data=data_dict)
    update_df = pd.concat([acct.df, df])
    acct.df = update_df


phil = create_acct("Phil", 100000)
elon = Asset()
elon.ticker = "TSLA"
elon.value = elon.newValue()

bto_asset(phil, elon.ticker, 5)
print(phil.df)
time.sleep(120)
x = 60
while x > 0:
    new_value = elon.newValue()
    if len(phil.asset) > 0:
        if new_value > (phil.asset[0].value + 1):  # adjust for bid/ask spread.
            print("selling")
            stc_asset(phil, "TSLA", phil.asset[0].shares)
        else:
            print("buy 5")
            bto_asset(phil, "TSLA", 5)
    else:
        bto_asset(phil, elon.ticker, 5)
    print(phil.df)
    x -= 1
    time.sleep(120)


