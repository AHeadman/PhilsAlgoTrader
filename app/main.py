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
        self.df = pd.DataFrame()

    def history(self, interval):
        ticker = yf.Ticker(self.ticker)
        hist = ticker.history(period="1D", interval=str(interval))
        return hist

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
                 'Change': [0],
                 'Shares': [0]}

    acct.df = pd.DataFrame(data=data_dict)
    return acct


def update_acct(acct):
    acct.valuation = acct.getValuation()
    if len(acct.asset) > 0:
        shares = acct.asset[0].shares
    else:
        shares = 0
    data_dict = {'Date-Time': datetime.datetime.now(),
                 'Name': [str(acct.name)],
                 'Cash': [float(acct.cash)],
                 'value': [acct.getValuation()],
                 'Change': [0],
                 'Shares': [shares]}
    df = pd.DataFrame(data=data_dict)
    update_df = pd.concat([acct.df, df])
    acct.df = update_df


phil = create_acct("Phil", 100000)
elon = Asset()
elon.ticker = "TSLA"

print(phil.df)

while datetime.datetime.utcnow().hour < 20:
    elon.df = elon.history("5m")
    open_last_min = elon.df.iloc[[-2]]["Open"]
    close_last_min = elon.df.iloc[[-2]]["Close"]
    momo = float(open_last_min) - float(close_last_min)
    print("momo = {}".format(momo))


    if momo > 0.5 and len(phil.asset) < 1:
        # Don't own anything with a rising trend
        print("No shares - rising trend")
        bto_asset(phil, "TSLA", 5)
        time.sleep(120)

    elif momo < -0.5 and len(phil.asset) < 1:
        # Don't own anything, falling trend
        print("No shares - falling trend")
        sto_asset(phil, "TSLA", 5)
        time.sleep(120)

    elif momo > 0.5 and phil.asset[0].shares > 0:
        # Own long share and price rises.
        print("sell - long")
        if elon.sellValue() > phil.asset[0].value:
            stc_asset(phil, "TSLA", phil.asset[0].shares)
            time.sleep(60)
        else:
            print("nevermind")
            print("Their price = {}, Our price (long) = {}".format(elon.sellValue(), phil.asset[0].value))
            time.sleep(60)

    elif momo < -0.5 and phil.asset[0].shares > 0:
        # Own long shares and prices falls.
        print("momo down, sell and short")
        stc_asset(phil, "TSLA", phil.asset[0].shares)
        sto_asset(phil, "TSLA", 5)
        time.sleep(120)

    elif momo > 0.5 and phil.asset[0].shares < 0:
        # Own short and price rises
        print("momo up, buy and long")
        btc_asset(phil, "TSLA", -phil.asset[0].shares)
        bto_asset(phil, "TSLA", 5)
        time.sleep(120)

    elif momo < -0.5 and phil.asset[0].shares < 0:
        # Own short and price falls
        print("Buy to close")
        if elon.buyValue() < phil.asset[0].value:
            btc_asset(phil, "TSLA", -phil.asset[0].shares)
            time.sleep(10)
        else:
            print("nevermind")
            print("Their price = {}, Our price (short) = {}".format(elon.buyValue(), phil.asset[0].value))
            time.sleep(120)

    else:
        # No momentum.  Pause and hold.
        print("No trend - Wait one minute.")
        for asset in phil.asset:
            if asset.type == "long" and elon.sellValue() > asset.value:
                print("consolidating profits - long")
                stc_asset(phil, "TSLA", phil.asset[0].shares)

            elif asset.type == "short" and elon.buyValue() < asset.value:
                print("consolidating profits - short")
                btc_asset(phil, "TSLA", phil.asset[0].shares)

        time.sleep(120)


    print(phil.df)


phil.df.to_csv("Test.csv")




