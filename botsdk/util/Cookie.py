import sys

import redis
from ujson import dumps, loads

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

    def getAllCookie(self):
        re = dict()
        for i in self.sql.keys("*"):
            re[i] = self._getCookie(i)
        return re

    # dict 非str
    def _getCookie(self, id: str, key):
        if key:
            if self.sql.hexists(id, key):
                return loads(self.sql.hget(id, key))
            return None
        else:
            ret = self.sql.hgetall(id)
            return {i: loads(ret[i]) for i in ret}

    # 无返回值
    def _setCookie(self, id: str, key: str, value):
        self.sql.hset(id, key, dumps(value))

    def getCookie(self, id: str, key: str = None):
        return self._getCookie(id, key)

    def setCookie(self, id: str, key: str, value):
        return self._setCookie(id, key, value)


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


def setCookie(id: str, key: str, value):
    getCookieDriver().setCookie(id, key, value)


async def asyncGetCookie(id: str, key: str = None):
    return await getCookieDriver().asyncGetCookie(id, key)


async def asyncSetCookie(id: str, key: str, value):
    await getCookieDriver().asyncSetCookie(id, key, value)
