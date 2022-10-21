import asyncio
import importlib
import json

from confluent_kafka import Consumer

from .util.Error import printTraceBack
from .util.Tool import getAttrFromModule


class BotHandle:
    def __init__():
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
                handle = getattr(module, msg["handle"])()
            except Exception:
                printTraceBack()
                return
            request = json.loads(msg["request"])
            request = getAttrFromModule(
                    request["botPath"],
                    request["botType"]
                )(request, request["responseChain"])
            try:
                await handle(request)
            except Exception:
                printTraceBack()
                return

    def run(self):
        asyncio.run(self.Loop())
