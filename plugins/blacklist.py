from botsdk.util.BotPlugin import BotPlugin
from botsdk.BotModule.MessageChain import MessageChain
from botsdk.util.Permission import getSystemPermissionAndCheck, permissionCmp


class plugin(BotPlugin):
    def __init__(self):
        super().__init__()
        self.name = "blacklist"
        self.addFilter(self.blackListCheck)
        self.addTarget("GroupMessage", "blacklist", self.blacklist)
        self.canDetach = True

    async def blacklist(self, request):
        '''/blacklist [add/remove] qq'''
        data = request.getFirstTextSplit()
        bot = request.getBot()
        groupid = request.getGroupId()
        cookie = request.getCookie("blackList")
        if cookie is None:
            cookie = []
        if "list" in data:
            await request.sendMessage(MessageChain().text(str(cookie)))
            return
        if len(data) < 3:
            await request.sendMessage(
                MessageChain().text("/blacklist [add/remove] qq"))
            return
        target = data[2]
        try:
            target = str(int(target))
            if target != data[2] or getSystemPermissionAndCheck(
                    target, "ADMINISTRATOR"):
                raise
        except Exception:
            await request.sendMessage(MessageChain().text("???"))
            return
        groupMemberList = await bot.memberList(groupid)
        groupMemberList = groupMemberList["data"]
        checkFlag = True
        if getSystemPermissionAndCheck(request.getSenderId(), "ADMINISTRATOR"):
            checkFlag = False
        else:
            for i in groupMemberList:
                if str(i["id"]) == target:
                    i["id"] = str(i["id"])
                    if permissionCmp(request.getPermission(), i["permission"]):
                        checkFlag = False
                    break
        if checkFlag:
            await request.sendMessage(MessageChain().text("权限不足或该qq不在群"))
            return
        if data[1] == "add":
            if target not in cookie:
                cookie.append(target)
        elif data[1] == "remove":
            if target in cookie:
                cookie.remove(target)
        request.setCookie("blackList", cookie)
        await request.sendMessage(MessageChain().text("完成"))

    async def blackListCheck(self, request):
        if request.getType() == "GroupMessage":
            cookie = request.getCookie("blackList")
            if cookie is not None and request.getSenderId() in cookie:
                return False
        return True


def handle(*args, **kwargs):
    return plugin(*args, **kwargs)
