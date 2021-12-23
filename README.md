# XyzB0ts
 基于[mirai-api-http](https://github.com/project-mirai/mirai-api-http)的bot框架  
 提供了对mirai-api-http的封装、消息分发与一些辅助功能  
 能够简单快速的上手bot功能的开发


# 快速开始
 [BOT部署](/docs/TOUSE.MD)  
 [插件制作](/docs/HOWTOSTART.MD)

## 一些链接
 [ADAPTER说明](/docs/ADAPTER.MD)  
 [更新记录](/docs/UPDATE.MD)

## 一个简单的插件实现
 在群中输入/hello时bot将发送hello  
```python
from botsdk.BotRequest import BotRequest
from botsdk.util.MessageChain import MessageChain
from botsdk.util.BotPlugin import BotPlugin


class plugin(BotPlugin):
    def __init__(self):
        super().__init__()
        self.name = "hello"
        self.addTarget("GroupMessage", "hello", self.hello)

    async def hello(self, request):
        await request.sendMessage(MessageChain().text("hello"))


def handle():
    return plugin()
```


# 鸣谢
 项目基于[mirai-api-http](https://github.com/project-mirai/mirai-api-http)  
 tool.pixiv使用了[hibiapi](https://github.com/mixmoe/HibiAPI)  
 tool.saucenao使用了[saucenao](https://saucenao.com/)


# Gitee地址
 [Gitee](https://gitee.com/d6e3032b/XyzB0ts)