"""
Name : LockManager
Author : blu
Time : 2022/3/7 08:19
Desc : 锁管理器封装
"""

import asyncio

from aiostar.spiders import BaseSpider
from aiostar.utils import singleton
from aiostar.utils.LogManager import LogManager

import threading


class SingletonType(type):
    _instance_lock = threading.Lock()

    def __call__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance"):
            with SingletonType._instance_lock:
                if not hasattr(cls, "_instance"):
                    cls._instance = super(SingletonType, cls).__call__(*args, **kwargs)
        return cls._instance


class LockManager(metaclass=SingletonType):

    def __init__(self):
        self.all_lock = {}

    def get_lock(self, name, spider=None):
        if not spider:
            lock_name = name
        elif isinstance(spider, BaseSpider):
            lock_name = f"{name}_{spider.spider_name}_{getattr(spider, 'message', None)}"
        else:
            lock_name = f"{name}_{str(spider)}"
        logger = LogManager().get_log("LockManager")
        # logger.info(f"{self},{id(self)}=={lock_name}===>all_lock:{self.all_lock}")
        if lock_name not in self.all_lock:
            self.all_lock[lock_name] = asyncio.Lock()
        logger.info(f"lock_name:{lock_name} 获取信号锁:{self.all_lock[lock_name]}")
        return self.all_lock[lock_name]
