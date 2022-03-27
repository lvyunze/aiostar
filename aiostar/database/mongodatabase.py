#!/usr/bin/env python
# -*- coding: utf-8 -*-
from motor.motor_asyncio import AsyncIOMotorClient


class MongoDatabase:
    def __init__(self, host=None, user=None, password=None, port=27017, database=None):
        self.client = AsyncIOMotorClient('mongodb://' + user + ':' + password + '@' + host + ':' + str(port))
        self.db = self.client[database]

    def conn_collection(self, collection=None):
        collection = self.db[collection]
        return collection

    @staticmethod
    async def insert_one_data(collection, document):
        result = await collection.insert_one(document)
        return result

    @staticmethod
    async def insert_many_data(collection, list_document):
        result = await collection.insert_many(list_document)
        return result

    @staticmethod
    async def find_data(collection, condition=None, sort_condition=None, skip_condition=None, limit_condition=None):
        if sort_condition and skip_condition and limit_condition:
            result = await collection.find(condition).sort(sort_condition).skip(skip_condition).limit(limit_condition)
        elif skip_condition and limit_condition:
            result = await collection.find(condition).skip(skip_condition).limit(limit_condition)
        elif sort_condition and limit_condition:
            result = await collection.find(condition).sort(sort_condition).limit(limit_condition)
        elif sort_condition and skip_condition:
            result = await collection.find(condition).sort(sort_condition).skip(skip_condition)
        elif sort_condition:
            result = await collection.find(condition).sort(sort_condition)
        elif skip_condition:
            result = await collection.find(condition).skip(skip_condition)
        elif limit_condition:
            result = await collection.find(condition).limit(limit_condition)
        else:
            result = await collection.find(condition)
        return result

    @staticmethod
    async def find_one_data(collection, condition=None):
        results = await collection.find_one(condition)
        return results

    @staticmethod
    async def update_one_data(collection, find_condition=None, set_condition=None):
        result = await collection.update_one(find_condition, set_condition)
        return result

    @staticmethod
    async def update_many_data(collection, find_condition=None, set_condition=None):
        results = await collection.update_many(find_condition, set_condition)
        return results

    @staticmethod
    async def delete_one_data(collection, find_condition=None):
        results = await collection.delete_one(find_condition)
        return results

    @staticmethod
    async def delete_many_data(collection, find_condition=None):
        results = await collection.delete_many(find_condition)
        return results
