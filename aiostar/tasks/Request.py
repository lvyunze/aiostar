"""
Name : Request
Author : blu
Time : 2022/3/7 08:19
Desc : 请求封装
"""
from aiostar.tasks import BaseTask


class Request(BaseTask):
    """
    Request 类
    该类存储request的相关信息及其传参
    需要什么的时候就修改什么
    """

    def __init__(self,
                 url,
                 callback=None,
                 method='GET',
                 headers=None,
                 data=None,
                 cookies=None,
                 meta=None,
                 encoding='utf-8',
                 params=None,
                 dont_filter=False,
                 errback=None,
                 flags=None,
                 proxy=None,
                 use_proxy=False,
                 timeout=30):
        self._encoding = encoding
        self.method = str(method).upper()
        self.url = url
        self.params = params
        self.data = data
        self.use_proxy = use_proxy
        self._is_parallel = True
        if callback is not None and not callable(callback):
            raise TypeError('callback must be a callable, got %s' % type(callback).__name__)
        if errback is not None and not callable(errback):
            raise TypeError('errback must be a callable, got %s' % type(errback).__name__)
        assert callback or not errback, "Cannot use errback without a callback"
        self.callback = callback
        self.errback = errback
        self.cookies = cookies or {}
        self.timeout = timeout
        self.proxy = proxy
        self.headers = headers
        self.dont_filter = dont_filter
        self._meta = dict(meta) if meta else dict()
        self.meta = self._meta
        self.flags = [] if flags is None else list(flags)

    def __str__(self):
        return "<Request %s %s>" % (self.method, self.url)

    __repr__ = __str__

    @property
    def domain(self):
        from urllib.parse import urlparse
        return urlparse(self.url).netloc

    @property
    def encoding(self):
        return self._encoding

    @property
    def is_parallel(self):
        return self._is_parallel


if __name__ == '__main__':
    rq = Request("https://www.baidu.com")
    print(rq)
    print(type(rq))
    from aiostar.spiders.hkex.nsall import Spider

    getattr(rq, '__iter__', None)
