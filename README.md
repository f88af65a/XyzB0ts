# XyzB0ts
 基于[mirai-api-http](https://github.com/project-mirai/mirai-api-http)的bot框架


# 插件开发
### botsdk.tool.BotPlugin
 BotPlugin中的注释非常详细  


### plugins中的样例
 plugins中有实现好的插件可以作为参考  


## 插件何时被调用
 插件被调用有三种方式:监听某一类型消息、监听某一关键字、过滤器  
 当收到符合条件的消息时会调用注册的回调函数


### 通过类型
 参考plugins.rechat  
 通过listenType直接赋值、listenType.append或者addType函数在listenType中添加监听信息  
 具体格式请参考注释，消息类型请参考[mirai-api-http 消息类型说明](https://github.com/project-mirai/mirai-api-http/blob/master/docs/api/MessageType.md)


### 通过关键字
 参考plugins.saucenao  
 通过listenTarget直接赋值、listenTarget.append或者addTarget函数在listenTarget中添加监听信息  
 具体格式请参考注释


#### 关键字如何判定
 参考botsdk.BotRoute.route  
 框架对关键字的判断是一个消息中首个`Plain`中`text` `split(" ")`后除去`控制字段`的形似`/命令 参数 参数...`的格式  
 现在一个完整的命令格式是`控制字段 /命令 参数 参数...`  
 具体判定方式请参考实现


### 过滤器
 参考plugins.blacklist  
 通过filterList直接赋值、filterList.append或者addFilter函数在filterList中添加监听信息  
 filter在调用后需要返回一个bool，若返回False则会直接结束route不再传递


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


# 配置文件
 配置文件夹默认位于./configs/  
 框架配置文件为./configs/config.json  
 插件配置文件为./configs/插件名/config.json  
 插件配置文件需要手动创建


# 数据持久化
 实现见botsdk.tool.Cookie  
 Cookie封装了操作SQLite3的方式保存经过base64编码的Json用于保存数据


### 获取群cookie
 获取方式为getCookieByDict(groupid)或getCookie(groupid, keyName)  


### 设置群cookie
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