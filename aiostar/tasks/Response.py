"""
Name : Request
Author : blu
Time : 2022/3/7 08:19
Desc : 响应封装
"""
from aiostar.tasks import BaseTask


class Response(BaseTask):
    """
    Response 作为 downloader的返回结果
    需要修改什么就修改什么
    """

    def __init__(self, request, origin_response, content, error_info=None) -> None:
        self.request = request
        self.response = origin_response
        self.content = content
        self.success = True if not error_info else False
        self.error_info = error_info
        self.is_updated = False  #
        self.is_repeat = False  # 是否修改过

    @property
    def status(self):
        return self.response.status

    @property
    def cookies(self):
        return self.response.cookies

    @property
    def body(self):
        return self.content.decode("utf-8")
