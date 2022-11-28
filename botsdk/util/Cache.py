from redis import asyncio as aioredis
from ujson import loads, dumps


class Cache:
    def __init__(self):
        pass

    async def SetCache(self, key, value):
        pass

    # 不存在则返回None
    async def GetCache(self, key):
        pass


class BaseCache(Cache):
    def __init__(self):
        self.redis = aioredis.Redis(
            host="localhost", port=6379, decode_responses=True)

    async def SetCache(self, key, value, ex=30):
        key = f"System:Cache:{key}"
        await self.redis.setex(key, ex, dumps(value))

    # 不存在则返回None
    async def GetCache(self, key):
        key = f"System:Cache:{key}"
        ret = await self.redis.get(key)
        if ret is not None:
            ret = loads(ret)
        return ret


cacheInstance = None


def GetCacheInstance():
    global cacheInstance
    if cacheInstance is None:
        cacheInstance = BaseCache()
    return cacheInstance
