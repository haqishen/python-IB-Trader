from ibapi.wrapper import EWrapper
from ibapi.client import EClient
from ibapi.contract import Contract
from ibapi.order import Order
import os
import sys
sys.path.append('../')
import config
import numpy as np
from pdb import set_trace as st


class IBClient(EClient):
    def __init__(self, wrapper):
        EClient.__init__(self, wrapper)
class IBWrapper(EWrapper):
    def __init__(self):
        EWrapper.__init__(self)


def createContract(symbol, sec_type='STK', exch='SMART', prim_exch='ISLAND', currency='USD'):
    contract = Contract()
    contract.symbol = symbol
    contract.secType = sec_type
    contract.exchange = exch
    contract.primaryExch = prim_exch
    contract.currency = currency
    return contract

def createOrder(action:str, quantity:float, limit_price=None):

    def LimitOrder(action:str, quantity:float, limit_price:float):
        # ! [limitorder]
        order = Order()
        order.action = action
        order.orderType = "LMT"
        order.totalQuantity = quantity
        order.lmtPrice = limit_price
        # ! [limitorder]
        return order

    def MarketOrder(action:str, quantity:float):
        #! [market]
        order = Order()
        order.action = action
        order.orderType = "MKT"
        order.totalQuantity = quantity
        #! [market]
        return order

    if limit_price is None:
        return MarketOrder(action, quantity)
    else:
        return LimitOrder(action, quantity, limit_price)


if __name__ == '__main__':
    checkData(['JDST', 'ERX'])