# coding:utf-8
from datetime import datetime, timedelta

root_dir = '/Users/haqishen/trade_ibapi/' 

symbols = ['QQQ']
black_list = []

today = datetime.today()
# summer time
RTH_begin = datetime(today.year,today.month,today.day,22,30,0)
# winter time
# RTH_begin = datetime(today.year,today.month,today.day,23,30,0)
RTH_end = RTH_begin + timedelta(hours=6,minutes=29)

account= 'UXXXXXX' 
cash = 20000.0

port = 4002 # IB Gateway
IP = '127.0.0.1'



