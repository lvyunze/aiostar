import datetime
import hashlib
import json
import time
import traceback
from functools import partial
from importlib import import_module, reload
from functools import wraps


def singleton(cls):
    _instance = {}

    @wraps(cls)
    def _singlenton(*args, **kargs):
        if cls not in _instance:
            _instance[cls] = cls(*args, **kargs)
        return _instance[cls]

    return _singlenton


def spider_factory(name, engine, xxl_id=None):
    """
    每次调用都是热加载
    后续测试如果耗时很严重 改为监听热加载
    :param name: 传参为 aiostarlord.spiders 底下的 spider的路径
    :return: 爬虫实例
    """
    if name.startswith("aiostar"):
        name = name.replace("aiostar.spiders.", "")
    module = import_module(
        '.'.join(
            [
                'aiostar.spiders',
                name,
            ]
        )
    )
    print(module)
    module = reload(module)
    spider = partial(getattr(module, 'Spider'),
                     name=name,
                     engine=engine,
                     xxl_id=xxl_id)()
    return spider


def md5(b, encoding="utf-8"):
    if isinstance(b, str):
        b = b.encode(encoding)
    m = hashlib.md5()
    m.update(b)
    return m.hexdigest()