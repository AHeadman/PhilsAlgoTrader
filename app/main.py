import pandas as pd
import yfinance as yf
import datetime
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
    stock.ticker = str(tick)
    stock.value = stock.buyValue()
    stock.shares = shares
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


phil = create_acct("Phil", 10000)

bto_asset(phil, "TSLA", 5)
print(phil.df)

stc_asset(phil, "TSLA", 5)
print(phil.df)

sto_asset(phil, "TSLA", 5)
print(phil.df)

btc_asset(phil, "TSLA", 5)
print(phil.df)


