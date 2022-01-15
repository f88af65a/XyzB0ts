# XyzB0ts
 一个简单的bot框架  
 通过简单的约定实现了对不同bot接口的统一抽象，实现了在一个框架中运行不同的bot  
 通过简单的api能够快速的上手bot功能的开发

## 框架主要功能
 1. 插件支持
 2. 基于角色的权限控制

## 支持的bot
 1. [mirai-api-http](https://github.com/project-mirai/mirai-api-http)
 2. [kaiheila](https://github.com/kaiheila/api-docs)(api较少 需要自己加adapter)

## 须知
 为了能够兼容更多类型的bot，本项目各个部分可能都需要进行较大的调整  
 最新的代码与功能会在dev分支中  
 部分文档可能会落后于实现

## BOT的开黑啦频道
 [邀请链接](https://kaihei.co/LUTGj9)

# 快速开始
 [BOT部署](/docs/TOUSE.MD)  
 [插件制作](/docs/HOWTOSTART.MD)

## 一些链接
 [ADAPTER说明](/docs/ADAPTER.MD)

## 一个简单的插件实现
 在群中输入/hello时bot将发送hello  
```python
from botsdk.util.BotPlugin import BotPlugin


class plugin(BotPlugin):
    def init(self):
        self.name = "hello"
        self.addTarget("GroupMessage", "hello", self.hello)
        self.addBotType("Mirai")

    async def hello(self, request):
        await request.sendMessage("hello")


def handle():
    return plugin()

```


# 鸣谢
 mirai来自[mirai-api-http](https://github.com/project-mirai/mirai-api-http)  
 kaiheila来自[kaiheila](https://github.com/kaiheila/api-docs)  
 plugins.pixiv使用了[hibiapi](https://github.com/mixmoe/HibiAPI)  
 plugins.saucenao使用了[saucenao](https://saucenao.com/)


# Gitee地址
 [Gitee](https://gitee.com/d6e3032b/XyzB0ts)