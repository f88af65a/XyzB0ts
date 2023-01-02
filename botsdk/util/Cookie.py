import sys

import motor.motor_asyncio
import pymongo
import redis
from redis import asyncio as aioredis
from ujson import dumps, loads

from .JsonConfig import getConfig
from .TimeTest import timeTest

'''
系统部分信息会储存于System中
Bot相关信息会存到{BotName}中
'''


class Cookie:
    # 存在则返回，不存在返回None
    def getCookie(self, id: str, key: str = None):
        pass

    def setCookie(self, id: str, key: str, value):
        pass

    async def asyncGetCookie(self, id: str, key: str = None):
        return self.getCookie(id, key)

    async def asyncSetCookie(self, id: str, key: str, value):
        self.setCookie(id, key, value)


class RedisCookie(Cookie):
    def __init__(self):
        self.sql = redis.Redis(
            host="localhost", port=6379, decode_responses=True)
        '''
        for i in self.sql.keys("*"):
            try:
                localData = loads(base64.b64decode(self.sql[i]).decode())
                self.sql.delete(i)
                for j in localData:
                    self.sql.hset(i, j, dumps(localData[j]))
            except Exception as e:
                print(e)
        '''

    # 不存在返回None，存入什么返回什么
    @timeTest
    def getCookie(self, id: str, key: str = None):
        if key:
            if self.sql.hexists(id, key):
                return loads(self.sql.hget(id, key))
            return None
        else:
            ret = self.sql.hgetall(id)
            return {i: loads(ret[i]) for i in ret}

    # 暂时无返回值
    @timeTest
    def setCookie(self, id: str, key: str, value):
        if value is None:
            self.sql.hdel(id, key)
        else:
            self.sql.hset(id, key, dumps(value))
            self.sql.save()


class AioRedisCookie(Cookie):
    def __init__(self):
        self.sql: aioredis.Redis = None

    async def init(self):
        self.sql = await aioredis.from_url(
            "redis://localhost:6379", db=0)

    # 不存在返回None，存入什么返回什么
    @timeTest
    async def AsyncGetCookie(self, id: str, key: str = None):
        if key:
            if await self.sql.hexists(id, key):
                return loads(await self.sql.hget(id, key))
            return None
        else:
            ret = await self.sql.hgetall(id)
            return {i.decode(): loads(ret[i]) for i in ret}

    # 暂时无返回值
    @timeTest
    async def AsyncSetCookie(self, id: str, key: str, value=None):
        if value is None:
            await self.sql.hdel(id, key)
        else:
            await self.sql.hset(id, key, dumps(value))
            await self.sql.save()


class AioMongoDBCookie(Cookie):
    def __init__(self):
        pass

    async def init(self):
        self.conn = motor.motor_asyncio.AsyncIOMotorClient(
            "mongodb://127.0.0.1:27017"
        )
        self.db = self.conn.get_database("XyzB0ts")
        self.dataSet = self.db.get_collection("Cookie")
        await self.dataSet.create_index(
            [("ID", pymongo.ASCENDING)]
        )

    # 不存在返回None，存入什么返回什么
    @timeTest
    async def AsyncGetCookie(self, id: str, key: str = None):
        result = await self.dataSet.find_one(
            {"ID": id}
        )
        if not result:
            return None
        if "_id" in result:
            del result["_id"]
        if "ID" in result:
            del result["ID"]
        if key:
            return result.get(key, None)
        return result

    # 暂时无返回值
    @timeTest
    async def AsyncSetCookie(self, id: str, key: str, value=None):
        if key == "_id" or key == "ID":
            return
        if value is None:
            await self.dataSet.update_one(
                {"ID": id},
                {"$unset": {key: None}}
            )
        else:
            await self.dataSet.update_one(
                {"ID": id},
                {"$set": {key: value}}
            )


cookieDriver = None


def getCookieDriver():
    global cookieDriver
    if cookieDriver is None:
        cookieDriver = getattr(
            sys.modules[__name__],
            getConfig()["cookieDriver"])()
    return cookieDriver


def getCookie(id: str, key: str = None):
    return getCookieDriver().getCookie(id, key)


def setCookie(id: str, key: str, value=None):
    getCookieDriver().setCookie(id, key, value)


asyncCookieDriver = None


async def InitAsyncCookieDriver(*args, **kwargs):
    global asyncCookieDriver
    asyncCookieDriver = AioMongoDBCookie()
    await asyncCookieDriver.init()


async def GetAsyncCookieDriver():
    global asyncCookieDriver
    if asyncCookieDriver is None:
        asyncCookieDriver = AioMongoDBCookie()
        await asyncCookieDriver.init()
    return asyncCookieDriver


async def AsyncGetCookie(id: str, key: str = None):
    return (await (await GetAsyncCookieDriver()).AsyncGetCookie(id, key))


async def AsyncSetCookie(id: str, key: str, value=None):
    (await (await GetAsyncCookieDriver()).AsyncSetCookie(id, key, value))
