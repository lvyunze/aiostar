"""
Name : DownloaderMiddlewareManager
Author : blu
Time : 2022/3/7 8:24
Desc :调度器
"""
import traceback

from aiostar.middleware import MiddlewareManager
import logging
logger = logging.getLogger(__name__)


class DownloaderMiddlewreManager(MiddlewareManager):
    component_name = 'downlaoder middleware'

    @classmethod
    def _get_mwlist_from_settings(cls, settings):
        return settings.get('downloader_middlewares', [])

    def _add_middleware(self, mw):
        hasattr(mw, 'process_request') and self.methods['process_request'].append(mw.process_request)
        hasattr(mw, 'process_response') and self.methods['process_response'].appendleft(mw.process_response)
        hasattr(mw, 'process_exception') and self.methods['process_exception'].appendleft(mw.process_exception)

    async def process_request(self, request, *args, **kwargs):
        await self._process_parallel('process_request', request, *args, **kwargs)

    async def process_response(self, response, *args, **kwargs):
        await self._process_parallel('process_response', response, *args, **kwargs)

    async def process_exception(self, request, exception, spider):
        spider.logger("downloader manager error:{}".format(str(traceback.format_exc())))
        return await self._process_parallel("process_exception", request, spider)
