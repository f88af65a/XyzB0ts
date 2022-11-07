# XyzB0ts
一个Bot框架

## 支持的bot
1. [mirai-api-http](https://github.com/project-mirai/mirai-api-http)
2. [kaiheila](https://github.com/kaiheila/api-docs)(api较少 需要自己加adapter)

## BOT的开黑啦频道
 [邀请链接](https://kaihei.co/LUTGj9)

# 快速开始
 [部署与依赖](/docs/TOUSE.MD)  
 [插件制作](/docs/HOWTOSTART.MD)

## 一些链接
 [ADAPTER说明](/docs/ADAPTER.MD)

## 一个简单的插件实现
 在群中输入/hello时bot将发送hello

```python
from botsdk.util.BotPlugin import BotPlugin


class handle(BotPlugin):
    def onLoad(self):
        self.name = "hello"
        self.addBotType("Mirai")
        self.addTarget("GroupMessage", "hello", self.hello)

    async def hello(self, request):
        "hello #hello"
        await request.sendMessage("hello")

```

# 鸣谢
 mirai来自[mirai-api-http](https://github.com/project-mirai/mirai-api-http)  
 kaiheila来自[kaiheila](https://github.com/kaiheila/api-docs)  
 plugins.pixiv使用了[hibiapi](https://github.com/mixmoe/HibiAPI)  
 plugins.saucenao使用了[saucenao](https://saucenao.com/)  
 mirlkoi来自[MirlKoi](https://iw233.cn/)

# Gitee地址
 [Gitee](https://gitee.com/d6e3032b/XyzB0ts)
