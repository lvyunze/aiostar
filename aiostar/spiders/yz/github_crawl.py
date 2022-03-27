#!/usr/bin/env python
# -*- coding: utf-8 -*-
from abc import ABC
import time
import re
import aiohttp
import asyncio
from aiostar.spiders import BaseSpider, Database
from retrying import retry
from bson import ObjectId
import json


class Spider(BaseSpider):
    md = Database(conn_type='mongodb').md
    _type = "restful"
    headers = {
        'Connection': 'keep-alive',
        'Cache-Control': 'max-age=0',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36',
        'Accept-Language': 'zh-CN,zh;q=0.9'
    }
    data_length = 0
    result = []

    @retry(stop_max_attempt_number=10, wait_random_min=30000, wait_random_max=120000)
    async def fetch(self, client, url):
        proxy = 'XXXXXX'
        async with client.get(url, proxy=proxy, headers=self.headers) as resp:
            text = await resp.text()
            print(url)
            dict_data = json.loads(text)
            if url.endswith('/readme'):
                return dict_data.get('content')
            return dict_data.get('items')

    async def get_basic_data(self, url):
        async with aiohttp.ClientSession() as client:
            time.sleep(0.5)
            dict_data = await self.fetch(client, url)
            items = []
            for item in dict_data:
                if item['language'] and 'python' in item['language'].lower():
                    html_url = item['html_url']
                    description = item['description']
                    owner = item['owner']['login']
                    avatar_url = item['owner']['avatar_url']
                    stars = item['stargazers_count']
                    watchers = item['watchers_count']
                    forks = item['forks_count']
                    created_at = item['created_at']
                    updated_at = item['updated_at']
                    language = item['language']
                    topics = item['topics']
                    full_name = item['full_name']
                    items.append(
                        [html_url, description, owner, avatar_url, stars, watchers, forks, created_at, updated_at,
                         language,
                         topics, full_name]
                    )
            return items

    async def get_readme_data(self, full_names):
        async with aiohttp.ClientSession() as client:
            base_url = 'https://api.github.com/repos/{}/readme'
            readme_contents = []
            readme_urls = [base_url.format(full_name) for full_name in full_names]
            self.headers.update({'Authorization': 'XXXXXXXXXXXXXXX'})
            for url in readme_urls:
                time.sleep(0.5)
                b64_content = await self.fetch(client, url)
                readme_contents.append(b64_content)
            return readme_contents

    async def save_data(self, data):
        collection = self.md.conn_collection(collection='repodb')
        res = await self.md.find_one_data(collection, {'project.html_url': data[0]})
        if res:
            set_condition = {
                '$set': {
                    'project.project_type': data[13],
                    'project.html_url': data[0],
                    'project.description': data[1],
                    'project.owner': data[2],
                    'project.avatar_url': data[3],
                    'project.stars': data[4],
                    'project.watchers': data[5],
                    'project.forks': data[6],
                    'project.created_at': data[7],
                    'project.updated_at': data[8],
                    'project.language': data[9],
                    'project.topics': data[10],
                    'project.full_name': data[11],
                    'project.readme_content': data[12]
                }
            }
            await self.md.update_one_data(collection, find_condition={"project.html_url": data[0]},
                                          set_condition=set_condition)
        else:
            document = {
                'project': {
                    'project_type': data[13], 'html_url': data[0], 'description': data[1], 'owner': data[2],
                    'avatar_url': data[3], 'stars': data[4], 'watchers': data[5], 'forks': data[6],
                    'created_at': data[7], 'updated_at': data[8], 'language': data[9], 'topics': data[10],
                    'full_name': data[11], 'readme_content': data[12]
                }
            }
            await self.md.insert_one_data(collection, document=document)

    async def on_message(self, msg):
        collection = self.md.conn_collection('repo_types')
        condition = {'_id': ObjectId('61d2a8dfe85000000d002982')}
        result = await self.md.find_one_data(collection=collection, condition=condition)
        types = result['types']
        base_urls = [f'https://api.github.com/search/repositories?q={x}&sort=stars&per_page=100&page=' for x in types]
        for idx, url in enumerate(base_urls):
            for i in range(1, 11):
                project_type = types[idx]
                url = url.rsplit('=', maxsplit=1)[0] + '=' + str(i)
                print(url)
                items = await self.get_basic_data(url)
                full_names = [item[-1] for item in items]
                readme_contents = await self.get_readme_data(full_names)
                all_data = [item + [readme_contents[key], project_type] for key, item in enumerate(items)]
                for key, data in enumerate(all_data):
                    print(key)
                    self.data_length += 1
                    self.result.append({'full_name': data[11], 'stars': data[4]})
                    await self.save_data(data)
                if len(items) < 100:
                    break

    def on_end(self):
        self.results = {
            "result": self.result,
            "length": self.data_length
        }
        print(self.results)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(Spider().on_message('github_spider'))
