import asyncio


class MessageBus:
    def __init__(self):
        self.topic = {}
        self.lock = asyncio.Lock()

    async def GetTopic(self, topic):
        await self.lock.acquire()
        if topic not in self.topic:
            self.topic[topic] = asyncio.Queue()
        ret = self.topic[topic]
        self.lock.release()
        return ret

    async def AsyncSendMessage(self, topic: str, message: bytes):
        await (await self.GetTopic(topic)).put(message)

    async def AsyncFetchMessage(self, topic: str):
        return await (await self.GetTopic(topic)).get()


messagebus = MessageBus()


def GetMessageBus():
    return messagebus
