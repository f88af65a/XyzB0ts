from botsdk.util.BotPlugin import BotPlugin
from EdgeGPT import Chatbot, ConversationStyle
import re


class plugin(BotPlugin):
    def onLoad(self):
        self.name = "edgegpt"
        self.addTarget("GroupMessage", "bing", self.edgechat)
        self.addBotType("Mirai")
        self.r = re.compile("\[\^[0-9]+\^\]")

    async def edgechat(self, request):
        "bing [文本]"
        await request.send("让我想一下")
        data = request.getFirstTextSplit()
        if len(data) < 2:
            await request.send(self.edgechat.__doc__)
            return
        msg = " ".join(data[1:])
        for i in range(1):
            try:
                bot = await Chatbot.create(cookie_path='./cookie')
            except Exception as e:
                print(e)
                break
            try:
                response = await bot.ask(
                    prompt=msg,
                    conversation_style=ConversationStyle.balanced,
                    wss_link="wss://sydney.bing.com/sydney/ChatHub"
                )
            except Exception:
                await request.send("超过每日次数限制")
                return
            try:
                if len(response["item"]["messages"]) < 2:
                    raise
            except Exception as e:
                print(e)
                break
            try:
                responseMsg = ""
                for i in response["item"]["messages"][1:]:
                    if "text" in i:
                        responseMsg += i["text"]
                while True:
                    s = self.r.search(responseMsg)
                    if s is None:
                        break
                    responseMsg = responseMsg[
                        :s.span()[0]] + responseMsg[s.span()[1]:]
                await request.send(responseMsg)
            except Exception as e:
                print(e)
                print(response)
                break
            return
        await request.send("响应错误")


def handle(*args, **kwargs):
    return plugin(*args, **kwargs)
