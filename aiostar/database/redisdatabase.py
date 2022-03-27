#!/usr/bin/env python
# -*- coding: utf-8 -*-
from aioredis.client import Redis
import asyncio


class RedisDatabase:
    def __init__(self, host=None, port=None, password=None, encoding='utf-8'):
        self.redis = asyncio.run(self.connect_redis("redis://" + host, port=port, password=password, encoding=encoding))

    @staticmethod
    async def connect_redis(host=None, port=None, password=None, encoding='utf-8'):
        redis = Redis()
        redis = await redis.from_url("redis://" + host, port=port, password=password, encoding=encoding)
        return redis

    async def get_value(self, key):
        redis = await self.connect_redis()
        value = await redis.get(key)
        await redis.close()
        return value

    async def set_value(self, key, value, expire=300):
        redis = await self.connect_redis()
        await redis.set(key, value)
        await redis.expire(key, expire)
        await redis.close()
