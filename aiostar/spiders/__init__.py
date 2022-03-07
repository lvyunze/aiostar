#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Name : spider
Author : blu
Time : 2022/3/7 08:19
Desc : 爬虫基类
"""
import json
import re
import traceback
import aiohttp

from aiostar.middleware import MiddlewareManager
from aiostar.tasks.Request import Request
from aiostar.tasks.Result import ResultTask
from aiostar.utils import md5


class BaseSpider(object):
    _type = "restful"
    DISABLE_MSG_TAG = False
    Single_Run = False

    settings = {
        "downloader_middlewares": [
            "aiostar.middleware.middlewares.UserAgentMiddleware",
            "aiostar.middleware.middlewares.RetryMiddleware",
            "aiostar.middleware.middlewares.RequestStatMiddleware",
            # "aiostar.utils.middlewares.ResponseFilterMiddleware"
        ]
    }

    def __init__(
            self,
            name=None,
            engine=None,
            xxl_id=None
    ):
        self.name = name
        self.engine = engine
        self.logger_name = "[{}] ".format(name)
        self.results = []
        self.success = False
        self.error_msg = "爬虫初始化"
        self.middlewares = MiddlewareManager.from_settings(self.settings)
        self.status = "PENDING"
        self.xxl_id = xxl_id

    @property
    def data(self):
        if self._type == "restful":
            return self.results
        returndata = []
        for task in self.results:
            if isinstance(task, ResultTask):
                returndata.append(json.loads(task.json))
            else:
                returndata.append(task)
        return returndata

    async def is_repeat(self, url, content):
        try:
            from aiostar.config.config import filter_content_api
            async with aiohttp.ClientSession() as session:
                params = {
                    "page": md5(url),
                    "md5": md5(content)
                }
                async with session.get(filter_content_api, params=params, timeout=1) as response:
                    jsondata = await response.json()
                    return jsondata['data']['is_exist']
        except:
            self.logger(traceback.format_exc())
            return False

    async def check_results_repeat(self, url, results):
        try:
            from aiostar.config.config import filter_urllist_api
            async with aiohttp.ClientSession() as session:
                params = {
                    "page": md5(url),
                    "list": results
                }
                import json
                async with session.post(filter_urllist_api, json=params, timeout=1) as response:
                    jsondata = await response.json()
                    return len(jsondata['data']["list"]) == 0
        except Exception as e:
            self.engine.logger.error("内容去重出错{}".format(traceback.format_exc()))
            return True

    def log(self, msg):
        from aiostar.tasks.TaskLog import TaskLog
        return TaskLog(f"[{getattr(self, 'message', None)}] " + str(msg))

    def logger(self, msg):
        from aiostar.utils.LogManager import LogManager
        logger = LogManager().get_log(self)
        logger.info(f"[{getattr(self, 'message', None)}] " + str(msg))

    def add_result_task(self, result):
        if isinstance(result, ResultTask):
            self.results.append(result)

    def on_end(self):
        self.status = "SUCCESS"
        yield self._merge_result()

    def on_message(self, msg):
        raise NotImplementedError

    async def test(self, msg):
        try:
            await self.engine._process_task_parallelly(self.on_message(msg), self)
            await self.engine._process_task_parallelly(self.on_end(), self)
        except Exception as e:
            print(e)
            self.status = "FAIL"
            self.exception = traceback.format_exc()

    async def run(self, msg):
        self.message = msg
        try:
            await self.engine._process_task_parallelly(self.middlewares.open_spider(self), self)
            if self.status == "PENDING":
                await self.engine._process_task_parallelly(self.on_message(msg), self)
                await self.engine._process_task_parallelly(self.on_end(), self)
            await self.engine._process_task_parallelly(self.middlewares.close_spider(self), self)
            await self.engine._process_task_parallelly(self.after_finish(), self)
        except Exception as e:
            await self.engine._process_task_parallelly(self.middlewares.spider_exception(self), self)
            self.error_msg = traceback.format_exc()
            self.logger("处理该msg失败:{}".format(msg))
            self.logger("爬虫爬取失败{}".format(traceback.format_exc()))
            self.status = "FAILED"

    async def start(self, msg):
        yield self.middlewares.open_spider(self)
        yield self.on_message(msg)
        yield self.on_end()
        yield self.middlewares.close_spider(self)

    def merge_result(self):
        return self.log("merge_result")

    def _merge_result(self):
        yield self.merge_result()

    def __str__(self):
        return re.findall("'(.*?)'", str(self.__class__))[0]

    def after_finish(self):
        yield self.log("execute after finish")

    @property
    def spider_name(self):
        return str(self).replace("aiostarlord.spiders.", "").replace(".Spider", "")

    @property
    def spider_path(self):
        return self.spider_name.replace(".", "/")

    async def download_file(
            self,
            url,
            save_path,
            callback,
            headers=None,
            cookies=None,
            meta={}
    ):
        default_headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36",
        }
        if not headers:
            headers = default_headers
        try:
            _meta = {
                'meta': meta,
                'url': url,
                'save_path': save_path,
                'callback': callback.__name__
            }
            yield Request(
                url=url,
                headers=headers,
                callback=self.save_file,
                meta=_meta,
                cookies=cookies
            )
        except Exception as e:
            print(e)
            yield self.log('[DOWNLOAD-EXCEPTION] {}'.format(traceback.format_exc()))

    async def save_file(self, request, response):
        _meta = request.meta
        try:
            assert response.status < 400
            with open(_meta['save_path'], 'wb') as f:
                f.write(response.content)
        except Exception as e:
            print(e)
            yield self.log('[DOWNLOAD-EXCEPTION] {}'.format(traceback.format_exc()))
        finally:
            request.meta = _meta.pop('meta')
            func = getattr(self, _meta['callback'])
            yield func(request, response)
