#!/usr/bin/env python
# -*- coding: utf-8 -*-
import aiomysql
import asyncio


class MysqlDatabase:
    def __init__(self, host='localhost', port=3306, user=None, password=None, db=None, loop=None, **kwargs):
        self._pool = self._connect(
            host=host,
            port=port,
            user=user,
            password=password,
            db=db,
            loop=loop,
            **kwargs
        )

    @staticmethod
    async def _connect(host='localhost', port=3306, user=None, password=None, db=None, loop=None, **kwargs):
        pool = await aiomysql.create_pool(
            host=host,
            port=port,
            user=user,
            password=password,
            db=db,
            loop=loop,
            **kwargs
        )
        return pool

    async def _execute(self, sql='', args=None, execute_type='', size=None):
        async with self._pool as conn:
            cursor = await conn.cursor()
            await cursor.excute(sql, args=args)
            if not execute_type:
                cursor.commit()
                return
            if execute_type == 'fetch_one':
                res = await cursor.fetchone()
            if execute_type == 'fetch_many':
                res = await cursor.fetchmany(size=size)
            if execute_type == 'fetch_all':
                res = await cursor.fetchall()
            return res

    def fetch_one(self, sql=''):
        res = asyncio.run(self._execute(sql=sql, execute_type='fetch_one'))
        return res

    def fetch_many(self, sql='', size=None):
        res = asyncio.run(self._execute(sql=sql, execute_type='fetch_many', size=size))
        return res

    def fetch_all(self, sql=''):
        res = asyncio.run(self._execute(sql=sql, execute_type='fetch_all'))
        return res

    def insert(self, sql=''):
        asyncio.run(self._execute(sql=sql))

    def delete(self, sql=''):
        asyncio.run(self._execute(sql=sql))
