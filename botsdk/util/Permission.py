from botsdk.util.Cookie import getCookieDriver
from botsdk.BotModule.Request import BotRequest
from botsdk.util.JsonConfig import getConfig


# 返回真为有权限,假为没权限
def permissionCheck(request: BotRequest, target: str):
    if (re := systemPermissionCheck(
            request, target, getConfig()["systemCookie"])) is not None:
        return re
    if getSystemPermissionAndCheck(
            request.getSenderId(), "ADMINISTRATOR"):
        return True
    if request.getType() == "GroupMessage":
        cookie = getCookieDriver().getCookieByDict(request.getId())
        if not (groupPermissionCheck(request, target, cookie)
                or groupMemberPermissionCheck(request, target, cookie)):
            return False
    return True


helpDict = {"OWNER": 3, "ADMINISTRATOR": 2, "MEMBER": 1, "None": -1}


def markToInt(mark: str):
    return helpDict[mark]


def permissionCmp(f, s):
    return helpDict[str(f)] > helpDict[str(s)]


def groupPermissionCheck(request: BotRequest, target: str, cookie):
    if request.getPermission() == "OWNER":
        return True
    if "groupPermission" not in cookie:
        return False
    if target in cookie["groupPermission"]:
        return (markToInt(request.getPermission())
                >= markToInt(cookie["groupPermission"][target]))
    elif "*" in cookie["groupPermission"]:
        return (markToInt(request.getPermission())
                >= markToInt(cookie["groupPermission"]["*"]))
    return False


# 格式为cookie["groupMemberPermission"] ["QQ"][命令,命令]
def groupMemberPermissionCheck(request: BotRequest, target: str, cookie):
    if ("groupMemberPermission" in cookie
            and str(request.getSenderId()) in cookie["groupMemberPermission"]
            and target in
            cookie["groupMemberPermission"][str(request.getSenderId())]):
        return True
    return False


# 系统权限所限制的指令在cookie["systemPermission"]["指令"]="权限"
# 用户权限在cookie["user"]["用户"]="权限"
def systemPermissionCheck(request: BotRequest, target: str, cookie):
    if "systemPermission" in cookie and target in cookie["systemPermission"]:
        if ("user" in cookie and str(request.getSenderId()) in cookie["user"]
                and markToInt(cookie["user"][str(request.getSenderId())])
                >= markToInt(cookie["systemPermission"][target])):
            return True
        return False
    return None


# 获取config中的user权限
def getPermissionFromSystem(qq):
    config = getConfig()
    qq = str(qq)
    if ("systemCookie" in config and "user" in config["systemCookie"]
            and qq in config["systemCookie"]["user"]):
        return config["systemCookie"]["user"][qq]
    return None


def getSystemPermissionAndCheck(qq, permission):
    if (re := getPermissionFromSystem(qq)) is not None:
        return permissionCmp(re, permission)
    return False
