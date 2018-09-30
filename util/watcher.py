# coding:utf-8
import sys
import time
import util
import config
from threading import Thread
from ibapi.utils import iswrapper


class Watcher(util.IBWrapper, util.IBClient):

    def __init__(self, IP, port, clientId, symbols):
        util.IBWrapper.__init__(self)
        util.IBClient.__init__(self, wrapper=self)
        self.IP = IP
        self.port = port
        self.clientId = clientId
        self.symbols = symbols
        self.data = {}
        self.Open = {}
        self.High = {}
        self.Low = {}
        self.access = []
        self.initialize()

    def getConnection(self):
        self.connect(self.IP, self.port, self.clientId)

    def initialize(self):
        for symbol in self.symbols:
            self.High[symbol] = -1.0
            self.Low[symbol] = 9999.

    @iswrapper
    def tickPrice(self, reqId, tickType, price, attrib):
        super().tickPrice(reqId, tickType, price, attrib)

        symbol = self.symbols[reqId]

        if symbol not in self.access and tickType in range(1, 5):
            print('| %s real-time data accessed!' % symbol)
            self.access.append(symbol)
        if tickType == 4:
            self.data[symbol] = price
            if price > self.High[symbol]:
                self.High[symbol] = price
            if price < self.Low[symbol]:
                self.Low[symbol] = price

    @iswrapper
    def tickSize(self, reqId, tickType, size):
        super().tickSize(reqId, tickType, size)

    def begin(self):
        for tickerId in range(len(self.symbols)):
            symbol = self.symbols[tickerId]

            contract = util.createContract(
                symbol,
                'STK',
                'SMART',
                'SMART',
                'USD'
            )
            self.reqMktData(tickerId, contract, "", False, False, [])

        thread = Thread(target=self.run)
        thread.start()
        setattr(self, "_thread", thread)


# FOR DEBUG
if __name__ == '__main__':

    sys.path.append('../')
    watcher = Watcher(config.IP, config.port, 2351, config.symbols)
    watcher.getConnection()
    watcher.begin()

    for i in range(50):
        # watcher.getMessage()
        print()
        print('| '+time.strftime('%H:%M'))
        for symbol in watcher.data.keys():
            print('| %s : %.2f' % (symbol, watcher.data[symbol]))

        time.sleep(10)

    watcher.disconnect()
