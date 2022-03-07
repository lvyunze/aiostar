"""
Name : UserAgentMiddleware
Author : blu
Time : 2022/3/7 08:19
Desc : 请求中间件
"""


class UserAgentMiddleware:

    def __init__(self):
        pass

    @classmethod
    def from_settings(cls, setting):
        return cls()

    async def process_request(self, request, *args, **kwargs):
        if None == request.headers:
            request.headers = dict()
        if not request.meta:
            request.meta = dict()
        if request.meta.get("change_header", True) == False:
            return
        if not request.headers.get("User-Agent"):
            request.headers[
                'User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36'
        headers = {
            "Pragma": "no-cache",
            "Cache-Control": "no-cache",
        }
        for k in headers:
            if k not in request.headers:
                request.headers[k] = headers[k]
