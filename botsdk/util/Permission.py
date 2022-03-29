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
        add: set = set(), need: set = set()):
    requestRole = await request.getRoles() | {"*"} | add
    userId = request.getUserId()
    if userId is None:
        return False
    # 系统权限判断
    systemCookie = getConfig()["systemCookie"]
    if userId in systemCookie["user"]:
        requestRole |= set(systemCookie["user"][userId])
    if "System:Owner" in requestRole or requestRole & need:
        return True
    if target in systemCookie["systemPermission"]:
        if set(systemCookie["systemPermission"][target]) & requestRole:
            return True
        else:
            return False
    # Onwer权限判断
    if request.getBot().getOwnerRole() in requestRole:
        return True
    # 确认id
    # 判断为群或者好友聊天获取不同的cookie
    localId = request.getId()
    if request.isSingle():
        localId = "System"
    # 角色判断
    cookie = request.getCookie("roles", localId)
    if cookie and userId in cookie:
        requestRole |= set(cookie[userId])
    if requestRole & need:
        return True
    childs = request.getId().split(":")[3:]
    # 根据permissionpp判断
    cookie = request.getCookie("permission", localId)
    if not cookie:
        return False
    m = 0
    while True:
        if ((target in cookie
            and (permissionRoles := set(cookie[target]))
            and (requestRole & permissionRoles
                 or ("*" in permissionRoles
                     and permissionRoles["*"] & requestRole)))
           or ("*" in cookie and set(cookie["*"]) & requestRole)):
            return True
        if m < len(childs) and f":{childs[m]}" in cookie:
            cookie = cookie[f":{childs[m]}"]
            m += 1
        else:
            break
    return False


async def roleCheck(request, roles, add=set()):
    requestRole = await request.getRoles() | {"*"} | add
    userId = request.getUserId()
    systemCookie = getConfig()["systemCookie"]
    if userId in systemCookie["user"]:
        requestRole |= set(systemCookie["user"][userId])
    localId = request.getId()
    if request.isSingle():
        localId = "System"
    cookie = request.getCookie("roles", localId)
    if cookie and userId in cookie:
        requestRole |= set(cookie[userId])
    return bool(requestRole & roles)
