"""
Name : RequestStatMiddleware
Author : blu
Time : 2022/3/7 08:19
Desc : 请求中间件
"""
import logging

logger = logging.getLogger(__name__)


class RequestStatMiddleware:

    def __init__(self):
        self.stat = dict()

    @classmethod
    def from_settings(cls, setting):
        if not hasattr(RequestStatMiddleware, "_instance"):
            RequestStatMiddleware._instance = RequestStatMiddleware()
        return RequestStatMiddleware._instance

    async def process_request(self, request, *args, **kwargs):
        if not kwargs:
            return
        if "spider" not in kwargs:
            return
        spider = kwargs['spider']
        class_flag = str(spider.__class__)
        if class_flag in self.stat:
            self.stat[class_flag] = self.stat[class_flag] + 1
        else:
            self.stat[class_flag] = 0
        logger.info("该爬虫{}共爬取了{}个页面".format(class_flag, self.stat[class_flag]))
