"""
Name : TaskHandler
Author : blu
Time : 2022/3/7 08:19
Desc : 任务处理封装
"""
from aiostar.downloader import BaseHttpDownloader
from aiostar.spiders import BaseSpider
from aiostar.tasks import BaseTask
from aiostar.tasks.Request import Request
from aiostar.tasks.Response import Response
from aiostar.utils.LogManager import LogManager
from aiostar.utils.decorator.async_time import with_timeout


class TaskHandler:

    def __init__(self, spider: BaseSpider):
        self.spider = spider
        self.engine = spider.engine
        self.downloader = BaseHttpDownloader(spider)
        self.log_manager = LogManager()

    async def RequestHandler(self, request, *args):
        response = await self.downloader.download(request, *args)
        if isinstance(response, Request):
            return response
        return request.callback(request, response)

    async def TaskLogHandler(self, tasklog, *args):
        self.log_manager.get_log(self.spider).info(tasklog.msg)

    async def ParallelTaskHandler(self, pt, *args):
        return pt.fun(*pt.args)

    async def _process(self, task, *args):
        if not isinstance(task, BaseTask):
            return
        taskhandler = getattr(self, task.__class__.__name__ + "Handler", None)
        if not taskhandler:
            raise NotImplementedError
        yield await taskhandler(task, *args)
