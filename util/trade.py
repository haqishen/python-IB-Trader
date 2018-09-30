# coding:utf-8
import time
import util
import config
from ibapi import comm  # read message returned from API
from ibapi.account_summary_tags import AccountSummaryTags
from ibapi.utils import iswrapper


class IBClientApp(util.IBWrapper, util.IBClient):

    def __init__(self, IP, port, clientId, logger=None):
        util.IBWrapper.__init__(self)
        util.IBClient.__init__(self, wrapper=self)
        self.IP = IP
        self.port = port
        self.clientId = clientId
        self.logger = logger
        self.info = {'positions': []}
        self.history_data = {}
        self.order_record = []
        self.permId2ord = {}

    def getConnection(self):
        self.connect(self.IP, self.port, self.clientId)
        self.reqIds(-1)
        self.getMessage(1)

    # ValidID
    def getNextValidId(self):
        self.valid_id += 1
        return self.valid_id

    @iswrapper
    def nextValidId(self, orderId):
        super().nextValidId(orderId)
        self.valid_id = orderId

    @iswrapper
    def error(self, reqId, errorCode, errorString):
        super().error(reqId, errorCode, errorString)
        if int(errorCode) >= 2000:
            return
        print('| Server return an error! reqId: %s, errorCode:%s, msg:%s' % (
            reqId, errorCode, errorString))

    def getAccInfo(self):
        self.info = {'positions': []}
        self.reqAccountSummary(102, "All", AccountSummaryTags.AllTags)
        self.reqPositions()
        time.sleep(2)
        self.cancelAccountSummary(102)
        self.getMessage(1)
        return self.info

    @iswrapper
    def accountSummary(self, reqId: int, account: str, tag: str, value: str,
                       currency: str):
        super().accountSummary(reqId, account, tag, value, currency)
        if (tag == 'TotalCashValue'):
            self.info['cash'] = value
        if (tag == 'NetLiquidation'):
            self.info['total'] = value

    @iswrapper
    def accountSummaryEnd(self, reqId: int):
        super().accountSummaryEnd(reqId)
        return

    @iswrapper
    def position(self, account, contract, position, avgCost):
        super().position(account, contract, position, avgCost)
        tmp = [contract.symbol, contract.secType, contract.currency, position, avgCost]
        self.info['positions'].append(tmp)

    @iswrapper
    def positionEnd(self):
        super().positionEnd()
        return

    def getHistoryData(self, reqId, symbol, queryTime, lastFor='10000 S', timeGap='5 secs'):
        contract = util.createContract(symbol, 'STK', 'SMART', 'SMART', 'USD')
        self.reqHistoricalData(
            reqId, contract, queryTime,
            lastFor, timeGap, 'TRADES', 1, 1, []
        )

    @iswrapper
    def historicalData(self, reqId, date, open, high,
                       low, close, volume, barCount,
                       WAP, hasGaps):
        super().historicalData(reqId, date, open, high, low, close, volume,
                               barCount, WAP, hasGaps)

        if reqId not in self.history_data.keys():
            self.history_data[reqId] = []

        single_row = '%s,%s,%s,%s,%s,%s\n' % (
            date, open, high, low, close, volume
        )
        self.history_data[reqId].append(single_row)

    @iswrapper
    def historicalDataEnd(self, reqId: int, start: str, end: str):
        super().historicalDataEnd(reqId, start, end)

    def sendOrderToServer(
        self,
        symbol,
        quantity,
        sec_type='STK',
        primary_exch='SMART',
        price=None
    ):

        contract = util.createContract(
            symbol,
            sec_type,
            'SMART',
            primary_exch,
            'USD'
        )
        action = "BUY" if quantity > 0 else "SELL"
        order = util.createOrder(action, abs(quantity), price)
        orderId = self.getNextValidId()

        print('|- Place order. ID is %d' % orderId)
        self.placeOrder(orderId, contract, order)
        self.order_record[orderId] = [symbol, action, False]

    @iswrapper
    def orderStatus(self, orderId, status, filled,
                    remaining, avgFillPrice, permId,
                    parentId, lastFillPrice, clientId,
                    whyHeld):
        super().orderStatus(orderId, status, filled, remaining,
                            avgFillPrice, permId, parentId,
                            lastFillPrice, clientId, whyHeld)

        if status != 'Filled' or self.order_record[orderId][2]:
            return
        symbol = self.order_record[orderId][0]
        action = self.order_record[orderId][1]
        self.order_record[orderId][2] = True

        try:
            msg = '| %s Filled! %s quantity:%d avgPrice:%.2f Total:%.2f\n' % (
                    time.strftime('%Y%m%d %H:%M:%S'),
                    action, filled, avgFillPrice,
                    filled * avgFillPrice
                )
            print(msg)
            self.logger.log(symbol, msg)
        except Exception:
            print('| Error in logger!')

    @iswrapper
    def openOrder(self, orderId, contract, order, orderState):
        super().openOrder(orderId, contract, order, orderState)
        # OpenOrder. ID: 2 UVXY STK @ SMART : BUY MKT 10.0 PreSubmitted
        print("OpenOrder. ID:", orderId, contract.symbol, contract.secType,
              "@", contract.exchange, ":", order.action, order.orderType,
              order.totalQuantity, orderState.status)
        order.contract = contract
        self.permId2ord[order.permId] = order

    @iswrapper
    def openOrderEnd(self):
        # ! [openorderend]
        super().openOrderEnd()
        print("OpenOrderEnd")
        # ! [openorderend]
        print("Received %d openOrders" % len(self.permId2ord))

    def getMessage(self, wait=3):
        time.sleep(wait)
        while not self.msg_queue.empty():
            text = self.msg_queue.get(block=True, timeout=0.2)
            fields = comm.read_fields(text)
            self.decoder.interpret(fields)


# FOR DEBUG
if __name__ == '__main__':
    app = IBClientApp(config.IP, config.port, clientId=230)
    app.getConnection()
    contract = util.createContract('UVXY', 'STK', 'SMART', 'SMART', 'USD')
    app.disconnect()
