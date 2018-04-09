# coding:utf-8
'''
main function
'''

from util.trade import IBClientApp
from util.watcher import Watcher
import config
from model.toy_model import Modle
from datetime import datetime, timedelta
import time

def main():

    # app for sending orders
    app = IBClientApp(config.IP, config.port, clientId=1)
    app.getConnection()

    # app for watching market price
    watcher = Watcher(config.IP, config.port, clientId=2, config.symbols)
    watcher.getConnection()
    watcher.begin() 

    # load model
    model = Modle(symbols = config.symbols,
                  cash = config.cash,
                  app = app)

    # 主循环
    is_begin = False
    t = time.time()
    while True:

        # get current time
        cur_time = datetime.today()

        # close position
        if cur_time > config.RTH_end:
            print('| Stop!')、
            model.stop()
            info = app.getAccInfo()
            break

        # run the model 5 seconds a time if is in Regular Trading Hours.
        if cur_time > config.RTH_begin:
            if not is_begin:
                is_begin = True
                print('| Begin!')
            model.run(watcher.data, cur_time)

        while time.time()-t < 5:
            time.sleep(0.0002)
        t+=5



if __name__ == '__main__':  

    main()





    