import sys

import redis
from redis import asyncio as aioredis
from ujson import dumps, loads

from .TimeTest import timeTest

from .JsonConfig import getConfig

'''
系统部分信息会储存于System中
Bot相关信息会存到{BotName}中
'''


class Cookie:
    def getAllCookie(self):
        pass

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

    @timeTest
    def getAllCookie(self):
        re = dict()
        for i in self.sql.keys("*"):
            re[i] = self.getCookie(i)
        return re

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

    @timeTest
    async def getAllCookie(self):
        re = dict()
        for i in await self.sql.keys("*"):
            re[i] = await self.getCookie(i)
        return re

    # 不存在返回None，存入什么返回什么
    @timeTest
    async def getCookie(self, id: str, key: str = None):
        if key:
            if await self.sql.hexists(id, key):
                return loads(await self.sql.hget(id, key))
            return None
        else:
            ret = await self.sql.hgetall(id)
            return {i: loads(ret[i]) for i in ret}

    # 暂时无返回值
    @timeTest
    async def setCookie(self, id: str, key: str, value=None):
        if value is None:
            await self.sql.hdel(id, key)
        else:
            await self.sql.hset(id, key, dumps(value))
            await self.sql.save()


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
    asyncCookieDriver = await aioredis.from_url(
            "redis://localhost:6379", db=0)


async def GetAsyncCookieDriver():
    return asyncCookieDriver


async def AsyncGetCookie(id: str, key: str = None):
    return await getCookieDriver().asyncGetCookie(id, key)


async def AsyncSetCookie(id: str, key: str, value):
    await getCookieDriver().asyncSetCookie(id, key, value)
