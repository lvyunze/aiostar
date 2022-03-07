"""
Author : blu
@Description : demo
数据源：http://www.boyar.cn/column/5.html
"""
import aiohttp
import asyncio
from lxml import etree
from aiostar.spiders import BaseSpider
from urllib.parse import urljoin
from aiostar.tasks.Request import Request
from aiostar.tasks.Result import ResultTask
import json
import datetime
import pandas as pd
from pprint import pprint
import re


class Spider(BaseSpider):
    _type = "restful"
    headers = {
        'Connection': 'keep-alive',
        'Cache-Control': 'max-age=0',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Referer': 'http://www.boyar.cn/column/6.html',
        'Accept-Language': 'zh-CN,zh;q=0.9',
    }
    end_data = ""
    date = ""

    async def fetch(self, client, url):
        async with client.get(url, headers=self.headers) as resp:
            assert resp.status == 200
            text = await resp.text()
            return text

    async def on_message(self, msg):
        async with aiohttp.ClientSession() as client:
            html = await self.fetch(client, 'http://www.boyar.cn/column/5.html')
            tree = etree.HTML(html)
            url = "http://www.boyar.cn"
            need = tree.xpath(r'//a[contains(text(), "港口大豆分销价格")]/@href')[:2]
            title = tree.xpath(r'//a[contains(text(), "港口大豆分销价格")]/text()')[0]
            pattern = re.compile(r"\d{4}(?:年)\d{1,2}(?:月)\d{1,2}(?:日)")
            date = pattern.findall(title)
            now_html = await self.fetch(client, urljoin(url, need[0]))
            now = pd.read_html(now_html)
            table = pd.DataFrame(now[0])
            self.end_data = [
                                {
                                    "name": result[1],
                                    "price": result[4],
                                    "up_down": result[3]
                                }
                                for result in table.itertuples()
                            ][1:]
            self.date = date[0]
            self.logger("日志测试")
            print(self.end_data)

    def on_end(self):
        self.results = {
            "result": self.end_data,
            "date": self.date
        }
        print(self.results)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(Spider().on_message('111'))
