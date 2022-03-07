"""
Name : CookieMiddleware
Author : blu
Time : 2022/3/7 08:19
Desc : cookie中间件
"""
from aiohttp.web_response import Response

from aiostar.tasks.Request import Request


class CookieMiddleware:

    def __init__(self):
        self.cookies = {}

    def load(self):
        pass

    def dump(self):
        pass

    @classmethod
    def from_settings(cls, setting):
        if not hasattr(CookieMiddleware, "_instance"):
            CookieMiddleware._instance = CookieMiddleware()
        return CookieMiddleware._instance

    async def process_request(self, request: Request, *args, **kwargs):
        if None is request.headers:
            request.headers = dict()
        if not request.cookies:
            request.cookies = self.cookies.get(request.domain, dict())

    async def process_response(self, response, *args, **kwargs):
        if response.cookies:
            self.cookies[response.request.domain] = response.cookies
