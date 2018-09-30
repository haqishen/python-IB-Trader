# coding:utf-8
'''
main function
'''

import time
import config
from util.watcher import Watcher
from model.toy_model import Model
from util.trade import IBClientApp
from datetime import datetime


def main():

    # app for sending orders
    app = IBClientApp(config.IP, config.port, 1)
    app.getConnection()

    # app for watching market price
    watcher = Watcher(config.IP, config.port, 2, config.symbols)
    watcher.getConnection()
    watcher.begin()

    # load model
    model = Model(
        symbols=config.symbols,
        cash=config.cash,
        app=app
    )

    # main iteration, run every 5 secs
    is_begin = False
    t = time.time()
    while True:

        # get current time
        cur_time = datetime.today()

        # close position and exit the program
        if cur_time > config.RTH_end:
            print('| Stop!')
            model.stop(watcher.data)
            info = app.getAccInfo()
            print(info)
            break

        # run the model 5 seconds a time if is in Regular Trading Hours.
        if cur_time > config.RTH_begin:
            if not is_begin:
                is_begin = True
                print('| Begin!')
            model.run(watcher.data, cur_time)

        while time.time() - t < 5:
            time.sleep(0.0002)
        t += 5


if __name__ == '__main__':
    main()
