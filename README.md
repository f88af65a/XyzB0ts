# XyzB0ts
 基于[mirai-api-http](https://github.com/project-mirai/mirai-api-http)的bot框架


# 插件开发
### botsdk.tool.BotPlugin
 BotPlugin中的注释非常详细  


### plugins中的样例
 plugins中有实现好的插件可以作为参考(但是没几句注释)


## 插件何时被调用
 参考botsdk.tool.BotRouter  
 插件被调用有三种方式:监听某一类型消息、监听某一关键字、通用处理  
 当收到符合条件的消息时会调用注册的回调函数


### 通过类型
 实现见botsdk.tool.BotRouter.TypeRouter  
 插件参考plugins.rechat  
 通过plugin.addType("消息类型", 回调函数)监听某一类型消息  
 具体格式请参考注释，消息类型请参考[mirai-api-http 消息类型说明](https://github.com/project-mirai/mirai-api-http/blob/master/docs/api/MessageType.md)


### 通过关键字
 实现见botsdk.tool.BotRouter.TargetRouter  
 参考plugins.saucenao  
 通过plugin.addTarget("消息类型","关键字", 回调函数)监听某一关键字  
 具体格式请参考注释，消息类型请参考[mirai-api-http 消息类型说明](https://github.com/project-mirai/mirai-api-http/blob/master/docs/api/MessageType.md)


#### 关键字如何判定
 参考botsdk.BotRoute.route  
 框架对关键字的判断是一个消息中首个`Plain`中`text` `split(" ")`后除去`控制字段`的形似`/命令 参数 参数...`的格式  
 现在一个完整的命令格式是`控制字段 /命令 参数 参数...`  
 具体判定方式请参考实现


### 通用处理
 实现见botsdk.tool.BotRouter.GeneralRouter  
 插件参考见plugins.format  
 通过plugin.addFilter(回调函数)或plugin.addFormat(回调函数)监听所有消息


### 对消息的封装BotRequest类
 实现见botsdk.BotRequest  
 BotRequest封装了发送的消息以及提供辅助函数，提供了sendMessage()向消息来源的群/人发送消息  
 可以通过BotRequest.getBot()与mirai-api-http交互


### MessageChain的封装
 实现见botsdk.tool.MessageChain  
 支持链式调用


### 与mirai-api-http交互
 实现见botsdk.Bot  
 该类对api进行了一定的封装，不够用就自己加吧


## 一个简单的插件实现
 在群中输入/hello时bot将发送hello  
```python
from botsdk.BotRequest import BotRequest
from botsdk.tool.MessageChain import MessageChain
from botsdk.tool.BotPlugin import BotPlugin

class plugin(BotPlugin):
    def __init__(self):
        super().__init__()
        self.name = "hello
        self.addTarget("GroupMessage", "hello", self.hello)"

    async def hello(self, request):
        await request.sendMessage(MessageChain().text("hello"))

def handle():
    return plugin()
```


# 配置文件
 配置文件夹默认位于./configs/  
 框架配置文件为./configs/config.json  
 插件配置文件为./configs/插件名/config.json  
 插件配置文件需要手动创建


# 数据持久化
 实现见botsdk.tool.Cookie  
 Cookie封装了操作SQLite3的方式保存经过base64编码的Json用于保存数据


### 获取cookie
 推荐的使用方式为getCookie(request.getId(), key)
 其中request.getId()对群消息返回值为"Group:群号",对好友消息返回值为"User:Q号"


### 设置cookie
 推荐的使用方式为setCookie(request.getId(), key, value)
 修改方式为setCookieByDict(groupid, cookie)或setCookie(groupid, cookie)  


# 权限系统
 实现见botsdk.tool.Permission  
 权限管理插件可以参考plugins.permission  
 内置权限共有系统权限与群内权限两种，可能会做好友消息的权限


### 权限
 系统权限与群内权限共分为三种:OWNER、ADMINISTRATOR、MEMBER  


## 系统权限
 系统权限保存于configs/config.json systemCookie字段中  


### user字段
 user字段保存Q号对应的`系统权限`  
 格式为"qq":"权限"


### systemPermission字段
 systemPermission字段保存命令执行所需的`系统权限`  
 格式为"命令":"权限"


## 群内权限
 群内权限保存于群Cookie中的groupPermission与groupMemberPermission  
 群内权限共有两种，指令权限与成员权限


### 指令权限
 指令权限指调用某个指令的最低权限，作用范围为所在群群


### 成员权限
 成员权限使某个成员可以使用某命令在某群


# 鸣谢
 项目基于[mirai-api-http](https://github.com/project-mirai/mirai-api-http)  
 tool.pixiv使用了[hibiapi](https://github.com/mixmoe/HibiAPI)  
 tool.saucenao使用了[saucenao](https://saucenao.com/)


 # Gitee地址
 [Gitee](https://gitee.com/d6e3032b/XyzB0ts)