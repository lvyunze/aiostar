"""
Name : RetryMiddleware
Author : blu
Time : 2022/3/7 08:19
Desc : 重试
"""
from aiostar.utils.LogManager import LogManager


class RetryMiddleware:
    @classmethod
    def from_settings(cls, setting):
        return cls()

    async def process_request(self, request, *args, **kwargs):
        if request.meta.get("donot_retry", True):
            return
        if None == request.meta.get("retry_num", None):
            request.meta['retry_num'] = 3
        request.meta['retry_num'] = request.meta['retry_num'] - 1
        logger = LogManager().get_log("retry")
        logger.info("[RETRYMIDDLEWARE] 重试爬取:{} 重试剩余次数:{}".format(request, request.meta['retry_num']))

    async def process_exception(self, request, *args, **kwargs):
        if request.meta.get("donot_retry", True):
            return
        if request.meta['retry_num'] <= 0:
            return
        logger = LogManager().get_log("retry")
        logger.info("[RETRYMIDDLEWARE] 重试爬取:{} 重试剩余次数:{}".format(request, request.meta['retry_num']))
        return request
