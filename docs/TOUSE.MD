# BOT部署
### 环境
 BOT开发环境为python3.10

### 依赖
 当前依赖:
 ```
 aiohttp
 pillow
 sqlite3/redis
 ```

### 部署
 mirai部署请前往[mirai-api-http](https://github.com/project-mirai/mirai-api-http)  
 BOT的部署只需要运行[start.py](/start.py)

### 配置文件
 BOT配置文件为[configs/config.json](/configs/config.json)  
 其中需要配置的部分为  
 ```json
 "account":[{"path":"localhost", "port":"", "qq":"","passwd":""}],
 ```
 其中path为http为api的路径,port为api的端口,qq为qq账号,passwd为qq密码
