"""
Name : LockManager
Author : blu
Time : 2022/3/7 08:19
Desc : 日志管理器封装
"""
import logging
import os
import time
from logging.handlers import WatchedFileHandler
from aiostar.utils import singleton


class BufferingFileHandler(WatchedFileHandler):

    def __init__(self, flush_interval=0.5, *args, **kwargs):
        self.flush_interval = flush_interval
        self._last_flush_time = 0
        super(BufferingFileHandler, self).__init__(*args, **kwargs)

    def flush(self, force=False):
        """
        Flushes the stream.
        """
        gap_t = self.flush_interval - (time.time() - self._last_flush_time)
        if gap_t > 0 and not force:
            return

        self.acquire()
        try:
            if self.stream and hasattr(self.stream, "flush"):
                self.stream.flush()
        finally:
            self.release()


@singleton
class LogManager:
    all = dict()

    @classmethod
    def get_log(cls, spider):
        log_name = str(spider).replace("aiostar.spiders.", "")[:-7]
        if isinstance(spider, str):
            log_name = spider
        if str(log_name) not in cls.all:
            format = '%(asctime)s [%(levelname)s] [' + str(log_name) + '] %(message)s'
            logger = logging.Logger(spider)
            # file_handler = BufferingFileHandler(
            #     flush_interval=0.5,
            #     filename=os.path.join(log_path, str(logname) + '.log')
            # )
            # file_handler.setFormatter(logging.Formatter(format))
            # logger.addHandler(file_handler)
            sh = logging.StreamHandler()
            sh.setFormatter(logging.Formatter(format))
            logger.addHandler(sh)
            # filename = os.path.join(log_path, str(log_name).replace(".", "/") + '.log')
            # os.makedirs(os.path.dirname(filename), exist_ok=True)
            # file_handler2 = logging.handlers.RotatingFileHandler(
            #     filename,
            #     maxBytes=10 * 1024 * 1024, backupCount=2)
            # file_handler2.setFormatter(logging.Formatter(format))
            # logger.addHandler(file_handler2)
            # logger.__setattr__('file_handler', file_handler)
            logger.setLevel(logging.INFO)
            cls.all[str(log_name)] = logger
        return cls.all[str(log_name)]
