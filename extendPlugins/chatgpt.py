from revChatGPT.revChatGPT import Chatbot

from botsdk.util.BotPlugin import BotPlugin
import threading
import uuid
import asyncio


class plugin(BotPlugin):
    def onLoad(self):
        self.name = "chatgpt"
        self.addTarget("GroupMessage", "chat", self.chat)
        self.addTarget("GROUP:9", "chat", self.chat)
        self.addBotType("Mirai")
        self.addBotType("Kaiheila")
        self.responseDict = dict()
        self.responseDictLock = threading.Lock()

    def init(self):
        self.token = self.getConfig()["token"]
        self.proxy = self.getConfig()["proxy"]

    def chatBotThread(self, message, requestUUID):
        config = {
            "session_token": self.token,
            "proxy": self.proxy
        }
        chatbot = Chatbot(config, conversation_id=None)
        for i in range(2):
            try:
                ret = chatbot.get_chat_response(message)["message"]
                break
            except Exception:
                ret = "请求异常"
        self.responseDictLock.acquire()
        self.responseDict[requestUUID] = ret
        self.responseDictLock.release()

    async def chat(self, request):
        "chat [文本]"
        data = request.getFirstTextSplit()
        if len(data) == 1:
            await request.sendMessage(self.chat.__doc__)
            return
        data = [data[0], " ".join(data[1:])]
        requestUUID = None
        while True:
            requestUUID = str(uuid.uuid4())
            self.responseDictLock.acquire()
            if requestUUID not in self.responseDict:
                self.responseDict[requestUUID] = None
                self.responseDictLock.release()
                break
            self.responseDictLock.release()
        thread = threading.Thread(
            target=self.chatBotThread, args=[data[1], requestUUID]
        )
        thread.start()
        while True:
            await asyncio.sleep(1)
            self.responseDictLock.acquire()
            if self.responseDict[requestUUID] is not None:
                retMessage = self.responseDict[requestUUID]
                del self.responseDict[requestUUID]
                self.responseDictLock.release()
                break
            self.responseDictLock.release()
        await request.send(retMessage)


def handle(*args, **kwargs):
    return plugin(*args, **kwargs)
