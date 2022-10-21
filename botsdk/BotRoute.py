import asyncio
from json import loads

from confluent_kafka import Consumer

from .util.BotPluginsManager import BotPluginsManager
from .util.BotRouter import GeneralRouter, TargetRouter, TypeRouter
from .util.Error import asyncTraceBack
from .util.TimeTest import asyncTimeTest
from .util.Tool import getAttrFromModule


class BotRoute:
    def __init__(self):
        self.pluginsManager = BotPluginsManager()
        self.router = [GeneralRouter(), TypeRouter(), TargetRouter()]

    @asyncTraceBack
    @asyncTimeTest
    async def route(self):
        c = Consumer({
            'bootstrap.servers': 'localhost:9092',
            'group.id': "targetHandleGroup"
        })
        c.subscribe(['routeList'])
        while True:
            msg = c.poll(1.0)
            if msg is None:
                continue
            if msg.error():
                print("Consumer error: {}".format(msg.error()))
                continue
            print('Received message: {}'.format(msg.value().decode('utf-8')))
            msg = loads(msg.value())
            request = getAttrFromModule(
                    msg[0]["botPath"],
                    msg[0]["botType"]
                )(msg[0], msg[1])
            for i in range(len(self.router)):
                if (re := await self.router[i].route(
                        self.pluginsManager, request,
                        None)) is not None and re is False:
                    return
                await asyncio.sleep(0)

    def getBot(self):
        return self.bot

    def run(self):
        asyncio.run(self.route())
