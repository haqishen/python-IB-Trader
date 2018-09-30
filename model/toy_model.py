'''
this is a toy model only for demonstrating the workflow of this repo.
'''


class Model():

    def __init__(self, symbols, cash, app):
        self.is_init = False
        self.symbols = symbols
        self.app = app
        self.cash = {}

        self.Open = {}
        self.Flag = {}
        self.Hold = {}
        for symbol in symbols:
            self.cash[symbol] = cash // len(symbols)
            self.Flag[symbol] = 0
            self.Hold[symbol] = 0

    def initiate(self, cur_price):
        for key in cur_price.keys():
            self.Open[key] = cur_price[key]
        self.is_init = True

    def run(self, cur_price, cur_time):
        if not self.is_init:
            self.initiate(cur_price)
        else:
            for symbol in cur_price.keys():
                if cur_price[symbol] > (self.Open[symbol] * 1.01) and self.Flag[symbol] != 1:
                    quantity = self.cash[symbol] // cur_price[symbol]
                    self.app.sendOrderToServer(symbol, quantity)
                    self.Hold[symbol] = quantity
                    self.Flag[symbol] = 1

    def stop(self, cur_price):
        for symbol in cur_price.keys():
            if self.Flag[symbol] != 0:
                quantity = self.Hold[symbol]
                self.app.sendOrderToServer(symbol, -quantity)
                self.Hold[symbol] = 0
                self.Flag[symbol] = 0
