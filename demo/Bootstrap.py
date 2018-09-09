# coding: utf-8
from dophon import boot
import threading

import schedule
s=schedule.Scheduler()

def sche():
    s.every(1).seconds.do(print,(666,))

def start():
    import time
    while True:
        s.run_pending()
        time.sleep(1)


from dophon.annotation import *

class BeanConfigs(BeanConfig):

    @bean()
    def call_beans(self):
        return bean_class()


class bean_class():
    def call(self):
        print('call')

with BeanConfigs() as b:
    pass


# 启动服务器
def run():
    import threading
    # sche()
    # threading.Thread(target=start).start()
    boot.bootstrap_app()
    # 启动服务器
    # boot.run_app_ssl()
    boot.run_app()


run()


