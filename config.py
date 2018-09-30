# coding:utf-8
from datetime import datetime, timedelta


root_dir = '/Users/haqishen/trader_ibapi/'

symbols = ['QQQ']  # symbols to trade
black_list = []

today = datetime.today()
# summer time in Japan is 22:30:00
# winter time in Japan is 23:30:00
RTH_begin = datetime(
    today.year,
    today.month,
    today.day,
    22, 30, 0
)
RTH_end = RTH_begin + timedelta(hours=6, minutes=29)

account = 'UXXXXXX'
cash = 20000.0

port = 4002  # IB Gateway
IP = '127.0.0.1'  # localhost
