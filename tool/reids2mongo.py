import asyncio
import motor.motor_asyncio
import pymongo
from redis import asyncio as aioredis
from ujson import loads


async def func():
    rd = await aioredis.from_url(
        "redis://localhost:6379", db=0
    )
    conn = motor.motor_asyncio.AsyncIOMotorClient(
        "mongodb://127.0.0.1:27017"
    )
    db = conn.get_database("XyzB0ts")
    dataSet = db.get_collection("Cookie")
    await dataSet.create_index(
        [("ID", pymongo.ASCENDING)]
    )
    ids = await rd.keys("*")
    for i in ids:
        keys = await rd.hgetall(i)
        data = {i.decode(): loads(keys[i]) for i in keys}
        data["ID"] = i.decode()
        await dataSet.insert_one(
            data
        )

asyncio.run(func())
