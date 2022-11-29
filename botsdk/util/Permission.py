from .JsonConfig import getConfig

'''
 一次Rquest的权限判断由发送者的角色、在Cookie中保存的角色和系统添加的角色
 发送者角色由request处理
 cookie中的角色在request初始化时从cookie["Permission"]获取
    cookie["Permission"]格式
    cookie["Permission"]={":id":{":id"={}, "命令名":["所需权限"]},"命令名":["所需权限"]}
 返回真为有权限,假为没权限
'''


async def permissionCheck(
        request, target: str,
        add: set = set()):
    requestRole = await request.getRoles() | {"*"} | add
    userId = request.getUserId()
    if userId is None:
        return False
    # 系统权限判断
    systemCookie = getConfig()["systemCookie"]
    if userId in systemCookie["user"]:
        requestRole |= set(systemCookie["user"][userId])
    if "System:Owner" in requestRole:
        return True
    if target in systemCookie["systemPermission"]:
        if set(systemCookie["systemPermission"][target]) & requestRole:
            return True
        else:
            return False
    # Onwer权限判断
    if not request.isSingle() and await request.isGroupOwner():
        return True
    # 从cookie中获取request的角色
    cookie = await request.AsyncGetCookie("roles")
    if cookie and userId in cookie:
        requestRole |= set(cookie[userId])
    # 获取cookie中的permission
    if request.isSingle():
        cookie = await request.AsyncGetCookie(
            "permission",
            request.getBot().getBotName()
        )
    else:
        cookie = await request.AsyncGetCookie("permission")
    if not cookie:
        return False
    # 如果有通匹符且有角色
    if "*" in cookie and set(cookie["*"]) & requestRole:
        return True
    # 命令有设置权限
    if target in cookie:
        permissionRoles = set(cookie[target])
        # 有权限
        if requestRole & permissionRoles:
            return True
        # 通匹
        if "*" in permissionRoles and permissionRoles["*"] & requestRole:
            return True
    return False


async def roleCheck(request, roles, add=set()):
    requestRole = await request.getRoles() | {"*"} | add
    userId = request.getUserId()
    systemCookie = getConfig()["systemCookie"]
    if userId in systemCookie["user"]:
        requestRole |= set(systemCookie["user"][userId])
    cookie = await request.AsyncGetCookie("roles")
    if cookie and userId in cookie:
        requestRole |= set(cookie[userId])
    return bool(requestRole & roles)


async def checkRoleById(request, id, roleName):
    requestRole = set()
    userId = request.getUserId()
    cookie = await request.AsyncGetCookie("roles", id)
    if cookie and userId in cookie:
        requestRole |= set(cookie[userId])
    if roleName in requestRole:
        return True
    return False
