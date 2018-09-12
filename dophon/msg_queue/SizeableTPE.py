import os
from concurrent.futures import ThreadPoolExecutor


class SizeableThreadPoolExecutor(ThreadPoolExecutor):
    _update_round = 2

    def update_worker_size(self):
        if len(self._threads) >= self._max_workers:
            # 容量达到极限自动扩容
            self._max_workers = len(self._threads) * self._update_round \
                if len(self._threads) \
                else (os.cpu_count() or 1) * 5
        elif len(self._threads) <= self._max_workers / 8:
            # 容量过剩自动缩容
            self._max_workers = len(self._threads) / self._update_round \
                if len(self._threads) \
                else (os.cpu_count() or 1) * 5

    @property
    def active_workers(self):
        return len(self._threads)

    def print_debug_info(self):
        print('当前线程:', len(self._threads), '---', self._threads)
        print('最大工人数:', self._max_workers)
