"""
Name : async_timeout
Author : blu
Time : 2022/3/7 08:19
Desc : 异步时间装饰器
"""
import asyncio

from async_timeout import timeout


def with_timeout(seconds=10):
    def decor(fun):
        async def wrapper(*args, **kwargs):
            async with timeout(seconds) as cm:
                results = await fun(*args, **kwargs)
            # print("超时",cm.expired)
            return results

        return wrapper

    return decor


if __name__ == '__main__':
    from aiostarlord.downloader import BaseHttpDownloader
    from aiostarlord.tasks.Request import Request


    async def t():
        x = Request("http://www.baidu.com")
        d = BaseHttpDownloader()
        _, m = await d.fetch(x)
        print(m)
        # print(m.error_info)


    loop = asyncio.get_event_loop()
    loop.run_until_complete(t())
