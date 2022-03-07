"""
Author : blu
Time : 2022/3/7 08:19
Desc : 下载中间件
"""
from collections import defaultdict, deque
from importlib import import_module


def load_object(path):
    try:
        dot = path.rindex('.')
    except ValueError:
        raise ValueError("Error loading object '%s': not a full path" % path)

    module, name = path[:dot], path[dot + 1:]
    mod = import_module(module)

    try:
        obj = getattr(mod, name)
    except AttributeError:
        raise NameError("Module '%s' doesn't define any object named '%s'" % (module, name))

    return obj


class MiddlewareManager(object):
    """Base class for implementing middleware managers"""

    component_name = 'base middleware'

    def __init__(self, *middlewares):
        self.middlewares = middlewares
        self.methods = defaultdict(deque)
        for mw in middlewares:
            self._add_middleware(mw)

    @classmethod
    def _get_mwlist_from_settings(cls, settings):
        # raise NotImplementedError
        return settings.get('spider_middlewares', [])

    @classmethod
    def from_settings(cls, settings, crawler=None):
        mwlist = cls._get_mwlist_from_settings(settings)
        middlewares = []
        enabled = []
        for clspath in mwlist:
            try:
                mwcls = load_object(clspath)
                mw = mwcls.from_settings(settings)
                middlewares.append(mw)
                enabled.append(clspath)
            except Exception as e:
                print(e)
                import traceback
                traceback.print_exc()
        return cls(*middlewares)

    @classmethod
    def from_crawler(cls, crawler):
        return cls.from_settings(crawler.settings, crawler)

    def _add_middleware(self, mw):
        if hasattr(mw, 'open_spider'):
            self.methods['open_spider'].append(mw.open_spider)
        if hasattr(mw, 'close_spider'):
            self.methods['close_spider'].appendleft(mw.close_spider)
        if hasattr(mw, 'spider_exception'):
            self.methods['spider_exception'].appendleft(mw.spider_exception)

    async def _process_parallel(self, method_name, obj, *args, **kwargs):
        need_return = False
        for method in self.methods[method_name]:
            obj_r = await method(obj, *args, **kwargs)
            if obj_r and obj_r.__class__ == obj.__class__:
                need_return = True
                obj = obj_r
        if need_return:
            return obj

    async def open_spider(self, spider):
        spider.logger(f"{getattr(spider,'message', None)} 中间件执行 open_spider")
        await self._process_parallel('open_spider', spider)

    async def close_spider(self, spider):
        spider.logger(f"{getattr(spider,'message', None)} 中间件执行 close_spider")
        await self._process_parallel('close_spider', spider)

    async def spider_exception(self, spider):
        spider.logger(f"{getattr(spider,'message', None)} 中间件执行 spider_exception")
        await self._process_parallel('spider_exception', spider)


if __name__ == '__main__':
    from aiostar.spiders.yz.demo import Spider

    s = Spider()
    mwlist = [
        "aiostar.utils.middlewares.SpiderResultMiddleware.SpiderResultMiddleware"
    ]
    setattr(s, 'settings', {'spider_middlewares': mwlist})
    mm = MiddlewareManager.from_crawler(s)
    print(mm.methods)
