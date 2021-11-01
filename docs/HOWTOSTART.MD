# 插件开发
### botsdk.util.BotPlugin
 实现见[botsdk.util.BotPlugin](botsdk/util.BotPlugin.py)
 所有插件应该先继承botsdk.util.BotPlugin以能够让框架能正常调用  


### 插件如何被初始化
 实现见[botsdk.util.BotPluginsManager](botsdk/util/BotPluginsManager.py)  
 插件的初始化在BotPluginsManager.loadPlugin中


### plugins中的样例
 plugins中有实现好的插件可以作为参考(但是没几句注释)


## 插件如何被调用
 实现见[botsdk.util.BotRouter](botsdk/util/BotRouter.py)  
 插件被调用有三种方式:监听某一类型消息、监听某一关键字、通用处理  
 以下将监听消息的回调函数称之为处理函数  
 当收到符合条件的消息时会调用注册的回调函数


### 监听类型
 实现见[botsdk.util.BotRouter.TypeRouter](botsdk/util/BotRouter.py)  
 参考见[plugins.rechat](plugins/rechat.py)  
 通过plugin.addType("消息类型", 回调函数)监听某一类型消息  
 具体格式请参考注释，消息类型请参考[mirai-api-http 消息类型说明](https://github.com/project-mirai/mirai-api-http/blob/master/docs/api/MessageType.md)


### 监听关键字
 实现见[botsdk.util.BotRouter.TargetRouter](botsdk/util/BotRouter.py)  
 参考见[plugins.saucenao](plugins/saucenao.py)  
 通过plugin.addTarget("消息类型","关键字", 回调函数)监听某一关键字  
 具体格式请参考注释，消息类型请参考[mirai-api-http 消息类型说明](https://github.com/project-mirai/mirai-api-http/blob/master/docs/api/MessageType.md)


#### 关键字判定
 对关键字的判断是一个消息中首个`Plain`中首个`text` `split(" ")`后除去`控制字段`的形似`/命令 参数 参数...`的格式  
 现在一个完整的命令格式是`控制字段 /命令 参数 参数...`  
 具体判定方式请参考实现


### 通用处理
 实现见[botsdk.util.BotRouter.GeneralRouter](botsdk/util/BotRouter.py)  
 参考见plugins.format  
 通过plugin.addFilter(回调函数)或plugin.addFormat(回调函数)监听所有消息


### BotRequest类
 实现见[botsdk.BotRequest](botsdk/BotRequest.py)  
 botsdk.BotRequest是一个功能众多的类，继承自dict，其内容为fetchMessage获取的消息,是处理函数处self外的唯一参数  
 除了继承自dict外，还实现了部分辅助函数提供便捷的使用    
 常用的有sendMessage、getCookie与setCookie  
 sendMessage可以直接向消息来源的人/群发送消息  
 getCookie和setCookie可以直接操作消息来源的Cookie  
 可以通过BotRequest.getBot()获取bot直接与mirai-api-http直接交互


### MessageChain的封装
 实现见[botsdk.util.MessageChain](botsdk/uitl/MessageChain.py)  
 一个提供对需要发送的消息进行封装的类，支持链式调用


### 与mirai-api-http交互
 实现见[botsdk.Bot](botsdk/Bot.py)  
 该类对mirai-api-http进行了一定的封装，不够用就自己加吧


# 配置文件
 配置文件夹默认位于./configs/  
 框架配置文件为./configs/config.json  
 插件配置文件为./configs/插件名/config.json  
 插件配置文件需要手动创建


# 数据持久化
 实现见botsdk.util.Cookie  
 Cookie封装了操作SQLite3的方式保存经过base64编码的Json用于保存数据


### 获取cookie
 推荐的使用方式为getCookie(request.getId(), key)
 其中request.getId()对群消息返回值为"Group:群号",对好友消息返回值为"User:Q号"


### 设置cookie
 推荐的使用方式为setCookie(request.getId(), key, value)
 修改方式为setCookieByDict(groupid, cookie)或setCookie(groupid, cookie)  


# 权限系统
 实现见botsdk.util.Permission  
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
