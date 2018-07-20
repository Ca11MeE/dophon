# coding: utf-8
from threading import Thread
import schedule, time
from dophon import logger

_sched = schedule.Scheduler()

"""
调度器
author:CallMeE
date:2018-06-01
"""

logger.inject_logger(globals())


class sech_obj:
    def __init__(self, fun, delay):
        self.__fun = fun
        self.__delay = delay

    def enter(self):
        global _scheds
        _sched.every(self.__delay).seconds.do(self.__fun)

    def run_target(self):
        return self.__fun


def run():
    while True:
        _sched.run_pending()
        time.sleep(1)


logger.info('xml自动更新调度启动')
Thread(target=run).start()
