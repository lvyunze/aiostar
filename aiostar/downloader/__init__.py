"""
Author : blu
Time : 2022/3/7 16:19
Desc : 下载器
"""
import traceback
import logging

logger = logging.getLogger(__name__)
import aiohttp

from aiostar.middleware.manager.DownloaderMiddlewareManager import DownloaderMiddlewreManager
from aiostar.tasks.Response import Response


class BaseDownloadHander():
    def __init__(self):
        pass

    async def fetch(self, request):
        kwargs = {}  # 用来存储aiohttp.get & aiohttp.post的参数
        if request.headers:
            headers = request.headers
        else:
            headers = {}
        kwargs['headers'] = headers  # 请求头

        # 时间延迟
        kwargs['timeout'] = request.timeout
        kwargs['proxy'] = request.proxy
        kwargs['cookies'] = request.cookies
        kwargs['params'] = request.params
        # 并发的控制 在这里会更好
        url = request.url
        conn = aiohttp.TCPConnector(verify_ssl=False)
        async with aiohttp.ClientSession(connector=conn) as session:
            if request.method == "POST":
                response = await session.post(url, data=request.data, **kwargs)
            else:
                response = await session.get(url, **kwargs)
            content = await response.read()
            return Response(
                request=request,
                origin_response=response,
                content=content
            )


class BaseHttpDownloader(object):

    def __init__(self, spider=None):
        self.hanlder = BaseDownloadHander()
        self.spider = spider
        self.middleware = None if not spider else DownloaderMiddlewreManager.from_crawler(spider)

    async def fetch(self, request):
        """
        request, Request, 请求
        """
        response = await self.hanlder.fetch(request)
        # response = await self.process_response(request, response)
        return request, response

    async def download(self, request, *args, **kwargs):
        if self.middleware:
            try:
                await self.middleware.process_request(request, *args, spider=self.spider)
            except:
                self.spider.logger("下载器中间件 process_request 出错{} ".format(traceback.format_exc()))
        try:
            response = await self.hanlder.fetch(request)
            if self.middleware:
                try:
                    await self.middleware.process_response(response, *args, spider=self.spider)
                except:
                    self.spider.logger("下載器中間件 process_response 出錯{}".format(traceback.format_exc()))
            return response
        except Exception as e:
            self.spider.logger("downloader fetch error :{}".format(traceback.format_exc()))
            if self.middleware:
                resp = await self.middleware.process_exception(request, e, self.spider)
                return resp


if __name__ == '__main__':
    from aiostar.tasks.Request import Request
    import asyncio

    loop = asyncio.get_event_loop()
    req = Request("https://www.baidu.com")

    m = loop.run_until_complete(BaseHttpDownloader().fetch(req))
    print(m)
