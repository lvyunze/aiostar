"""
Name : async_timeout
Author : blu
Time : 2022/3/7 08:19
Desc : 中间件封装
"""


class BasePulgIn:
    """
    插件的基类
    对函数的输入输出进行处理
        执行目标函数前 先执行before 改造传参
        返回结果后 执行after 改造结果
    """
    def before(self, *args, **kwargs):
        """
        对输入的预处理
        :param args:
        :param kwargs:
        :return:
        """
        raise NotImplementedError

    def after(self, *args, **kwargs):
        """
        对输出的预处理
        :param args:
        :param kwargs:
        :return:
        """
        raise NotImplementedError


def middleware(cls_attr='pulgs', async_sign=True):
    """
    cls_attr 判断类中的该属性
    :param cls_attr:
    :param async_sign: 是否是异步函数
    :return:
    """
    def decor(f):
        # 异步装饰器
        async def async_wrapper(cls, *args, **kwargs):
            if not hasattr(cls, cls_attr):
                return await f(cls, *args, **kwargs)
            mw_dict = getattr(cls, cls_attr)
            for k in mw_dict:
                args, kwargs = await mw_dict[k].before(*args, **kwargs)
            res = await f(cls, *args, **kwargs)
            for k in mw_dict:
                res = await mw_dict[k].after(res)
            return res

        # 同步函数的装饰器
        def wrapper(cls, *args, **kwargs):
            if not hasattr(cls, cls_attr):
                return f(cls, *args, **kwargs)
            mw_dict = getattr(cls, cls_attr)
            for k in mw_dict:
                args, kwargs = mw_dict[k].before(*args, **kwargs)
            res = f(cls, *args, **kwargs)
            for k in mw_dict:
                res = mw_dict[k].after(res)
            return res

        if async_sign:
            return async_wrapper
        return wrapper

    return decor


if __name__ == '__main__':
    class UAM(BasePulgIn):
        async def before(self, *args, **kwargs):
            request = args[0]
            request.headers = {
                'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
                              " Chrome/83.0.4103.116 Safari/537.36",
            }
            return args, kwargs

        async def after(self, *args, **kwargs):
            resp = args[0]
            resp.content = resp.content.decode("utf-8")
            print(resp.content)
            return resp


    from aiostar.downloader import BaseHttpDownloader
    from aiostar.tasks.Request import Request
    import asyncio


    class TestHttpDownloader(BaseHttpDownloader):

        @middleware('pulgs')
        def fetch(self, request):
            return super().fetch(request)


    loop = asyncio.get_event_loop()
    req = Request("https://www.baidu.com")
    bd = TestHttpDownloader()
    setattr(bd, 'pulgs', {'uam': UAM()})
    m = loop.run_until_complete(bd.fetch(req))
    print(m)
