# coding:utf-8
import sys
sys.path.append('../')
from ibapi import (decoder, reader, comm) # read message returned from API
from ibapi.common import * # TickerID
from ibapi.account_summary_tags import * 
from ibapi.utils import iswrapper
from ibapi.contract import Contract
from ibapi.order import Order
from ibapi.order_state import OrderState
# from ibapi.wrapper import EWrapper
# from ibapi.client import EClient
import util
import config
import datetime
import time
from pdb import set_trace as st


class IBClientApp(util.IBWrapper, util.IBClient):

    def __init__(self, IP, port, clientId, logger=None):
        util.IBWrapper.__init__(self)
        util.IBClient.__init__(self, wrapper=self)
        self.IP = IP
        self.port = port
        self.clientId = clientId
        self.logger = logger
        self.info = {'positions':[]}
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
    def nextValidId(self, orderId: int):
        super().nextValidId(orderId)
        self.valid_id = orderId

    @iswrapper
    def error(self, reqId:TickerId, errorCode:int, errorString:str):
        super().error(reqId, errorCode, errorString)
        if int(errorCode) >= 2000:
            return
        print('| Server return an error! reqId:%s, errorCode:%s, msg:%s' % \
                    (reqId, errorCode, errorString))


    def getAccInfo(self):
        self.info = {'positions':[]}
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
    def position(self, account: str, contract: Contract, position: float,
                 avgCost: float):
        super().position(account, contract, position, avgCost)
        tmp = [contract.symbol, contract.secType, contract.currency, position, avgCost]
        self.info['positions'].append(tmp)
        、
    @iswrapper
    def positionEnd(self):
        super().positionEnd()
        return

    #--------------------

    def getHistoryData(self, reqId, symbol, queryTime, lastFor='10000 S', timeGap='5 secs'):
        contract = util.createContract(symbol, 'STK', 'SMART', 'SMART', 'USD')
        self.reqHistoricalData(reqId, contract, queryTime,
                lastFor, timeGap, 'TRADES', 1, 1, [])
        

    @iswrapper
    def historicalData(self, reqId: TickerId, date: str, open: float, high: float,
                       low: float, close: float, volume: int, barCount: int,
                       WAP: float, hasGaps: int):
        super().historicalData(reqId, date, open, high, low, close, volume,
                               barCount, WAP, hasGaps)

        if reqId not in self.history_data.keys():
            self.history_data[reqId] = []

        single_row = '%s,%s,%s,%s,%s,%s\n' % \
                (date, open, high, low, close, volume)
        self.history_data[reqId].append(single_row)

    @iswrapper  
    def historicalDataEnd(self, reqId: int, start: str, end: str):
        super().historicalDataEnd(reqId, start, end)

    # ------------------
    
    def sendOrderToServer(self, symbol, quantity, sec_type='STK', primary_exch='SMART', price=None):

        contract = util.createContract(symbol, sec_type, 'SMART', primary_exch, 'USD')
        action = "BUY" if quantity > 0 else "SELL"
        order = util.createOrder(action, abs(quantity), price)
        orderId = self.getNextValidId()
        
        print('|- Place order. ID is %d' % orderId)
        self.placeOrder(orderId, contract, order)
        self.order_record[orderId] = [symbol, action, False]


    @iswrapper
    def orderStatus(self, orderId: OrderId, status: str, filled: float,
                    remaining: float, avgFillPrice: float, permId: int,
                    parentId: int, lastFillPrice: float, clientId: int,
                    whyHeld: str):
        super().orderStatus(orderId, status, filled, remaining,
                            avgFillPrice, permId, parentId, lastFillPrice, clientId, whyHeld)

        if status!='Filled' or self.order_record[orderId][2]:
            return
        symbol = self.order_record[orderId][0]
        action = self.order_record[orderId][1]
        self.order_record[orderId][2] = True 

        try:
            msg = '| %s Filled! %s quantity:%d avgPrice:%.2f Total:%.2f\n' % \
                (time.strftime('%Y%m%d %H:%M:%S'), action, filled, avgFillPrice, filled*avgFillPrice)
            print (msg)
            logger.log(symbol, msg)
        except:
            print('| Error in logger!')


    @iswrapper 
    def openOrder(self, orderId: OrderId, contract: Contract, order: Order,
                  orderState: OrderState):
        super().openOrder(orderId, contract, order, orderState)
        # OpenOrder. ID: 2 UVXY STK @ SMART : BUY MKT 10.0 PreSubmitted
        print("OpenOrder. ID:", orderId, contract.symbol, contract.secType,
              "@", contract.exchange, ":", order.action, order.orderType,
              order.totalQuantity, orderState.status)
        order.contract = contract
        self.permId2ord[order.permId] = order
    @iswrapper
    # ! [openorderend]
    def openOrderEnd(self):
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
 

### DEBUG ###
if __name__ == '__main__':
    app = IBClientApp(config.IP, config.port, clientId=230)
    app.getConnection()
    contract = util.createContract('UVXY', 'STK', 'SMART', 'SMART', 'USD')
    

    ## 历史数据DEBUG
    # queryTime = (datetime.datetime.today() -
    #                      datetime.timedelta(days=3)).strftime("%Y%m%d %H:%M:%S")
    # app.reqHistoricalData(101, contract, queryTime, '100 S', '5 secs', 'TRADES', 1, 1, [])
    # queryTime = (datetime.datetime.today() -
    #                      datetime.timedelta(days=3)).strftime("%Y%m%d %H:%M:%S")  
    # app.getHistory_data(['UVXY'], queryTime)
    # app.getMessage(3)

    ## 账户信息DEBUG
    # app.reqAccountSummary(102, "All", AccountSummaryTags.AllTags)
    # time.sleep(3)
    # app.cancelAccountSummary(102)
    # app.getMessage(3)

    ## 账户持仓DEBUG
    # app.reqPositions()
    # app.getMessage(3)

    ## real time bar
    # app.reqRealTimeBars(3101, contract, 5, "MIDPOINT", True, [])
    # app.getMessage(3)

    ## ValidId
    # app.getNextValidId()
    # print(app.valid_id)
    # app.getNextValidId()
    # print(app.valid_id)
    # app.getNextValidId()
    # print(app.valid_id)

    # 发送订单
    # app.sendOrderToServer('UVXY', 10)
    # app.getMessage(5)

    # 查看订单
    # app.reqAllOpenOrders()
    # app.getMessage(3)
    # app.reqGlobalCancel()
    # app.getMessage(5)

    app.disconnect()
