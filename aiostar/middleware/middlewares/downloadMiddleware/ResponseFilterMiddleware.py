"""
Name : ResponseFilterMiddleware
Author : blu
Time : 2022/3/7 08:19
Desc : 请求中间件
"""
import asyncio
import hashlib
import traceback
from urllib.parse import urljoin
import logging

from aiostar.utils import md5

logger = logging.getLogger(__name__)
import aiohttp

from aiostar.tasks.Request import Request
from aiostar.config.config import filter_host
from aiostar.tasks.Response import Response


class ResponseFilterMiddleware:

    def __init__(self):
        self.session = aiohttp.ClientSession()
        self.filter_api = urljoin(filter_host, "filtrate/page")

    async def filter(self, response):
        params = {
            "page": md5(response.request.url),
            "md5": md5(response.content)
        }
        resp = await self.session.get(
            url=self.filter_api,
            params=params,
            timeout=5
        )
        filter_data = await resp.json()
        is_exist = filter_data.get("data", {}).get("is_exist", False)
        response.is_repeat = is_exist

    @classmethod
    def from_settings(cls, setting):
        if not hasattr(ResponseFilterMiddleware, "_instance"):
            ResponseFilterMiddleware._instance = ResponseFilterMiddleware()
        return ResponseFilterMiddleware._instance

    async def process_response(self, response, *args, **kwargs):
        try:
            await self.filter(response)
        except:
            logger.error("調用去重接口出錯:{}", traceback.format_exc())
