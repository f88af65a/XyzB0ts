# XyzB0ts
基于[mirai-api-http](https://github.com/project-mirai/mirai-api-http)的bot框架


# 插件开发
### botsdk.tool.BotPlugin
BotPlugin中的注释非常详细


### plugins中的样例
plugins中有实现好的插件可以作为参考


### 插件何时被调用
插件被调用有三种方式:监听某一类型消息、监听某一关键字、过滤器。 
当收到符合条件的消息时会调用注册的回调函数


#### 通过类型
参考plugins.rechat  
通过listenType直接赋值、listenType.append或者addType装饰器在listenType中添加监听信息  
具体格式请参考注释


#### 通过关键字
参考plugins.saucenao  
通过listenTarget直接赋值、listenTarget.append或者addTarget装饰器在listenTarget中添加监听信息  
具体格式请参考注释  


##### 关键字如何判定
参考botsdk.BotRoute.route  
框架对关键字的判断是一个消息中首个`Plain`中`text``split(" ")`后除去`控制字段`的形似`/命令 参数 参数`的格式  
现在一个完整的命令格式是`控制字段 /命令 参数 参数...`  
具体判定方式请参考实现


#### 过滤器
参考plugins.blacklist  
通过filterList直接赋值、filterList.append或者addFilter装饰器在filterList中添加监听信息  
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

# Gitee地址
[Gitee](https://gitee.com/d6e3032b/XyzB0ts)