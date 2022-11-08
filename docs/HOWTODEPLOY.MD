# BOT部署
### 环境
 BOT开发环境为python3.10  
 此外还需要:  
 ```
 Redis  
 Kafka  
 Zookeeper
 ```

### 依赖
 Python依赖[requirements](requirements)  

### 部署
 mirai部署请前往[mirai-api-http](https://github.com/project-mirai/mirai-api-http)  
 BOT的单机部署可以使用[xyzb0ts.py](/xyzb0ts.py)

### 配置文件
 BOT配置文件为[configs/config.json](/configs/config.json)  
 其中需要配置的部分为  
 ```json
 "account":[
        {
            "path":"填写API的URL",
            "port":"API的端口",
            "qq":"QQ帐号",
            "passwd":"HTTPAPI的密码"
        }
    ]
 ```
