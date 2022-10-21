import asyncio
import importlib
import json

from confluent_kafka import Consumer

from .util.Error import printTraceBack
from .util.Tool import getAttrFromModule


class BotHandle:
    def __init__(self):
        pass

    async def Loop(self):
        c = Consumer({
            'bootstrap.servers': 'localhost:9092',
            'group.id': "targetHandleGroup"
        })
        c.subscribe(['targetHandle'])
        while True:
            msg = c.poll(1.0)
            if msg is None:
                continue
            if msg.error():
                print("Consumer error: {}".format(msg.error()))
                continue

            print('Received message: {}'.format(msg.value().decode('utf-8')))
            msg = json.loads(msg.value())
            try:
                module = importlib.reload(importlib.import_module(msg["path"]))
                plugin = getattr(module, "handle")()
                handle = getattr(plugin, msg["handle"])
            except Exception:
                printTraceBack()
                return
            request = msg["request"]
            request = getAttrFromModule(
                    request[0]["botPath"],
                    request[0]["botType"]
                )(request[0], request[1])
            try:
                await handle(request)
            except Exception:
                printTraceBack()

    def run(self):
        asyncio.run(self.Loop())
