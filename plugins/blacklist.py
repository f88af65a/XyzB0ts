import botsdk.Bot
import botsdk.BotRequest
from botsdk.tool.MessageChain import MessageChain
from botsdk.tool.Cookie import getCookie, setCookie
from botsdk.tool.BotPlugin import BotPlugin
from botsdk.tool.Permission import permissionCmp
from botsdk.tool.Permission import GetSystemPermissionAndCheck

class plugin(BotPlugin):
    def __init__(self):
        super().__init__()
        self.listenType = []
        #[["type1",func],["type2",func],...,["typen",func]]
        self.listenTarget = [["GroupMessage", "blacklist", self.blacklist], \
                ]
        #[["type1","target",func],["type2","target",func],...,["typen","target",func]]
        self.filterList = [self.blackListCheck]
        self.name = "blacklist"
        #"插件名称"
        self.info = "黑名单管理"
        #"插件信息"
        self.help = "/blacklist [add/remove] qq"
        #"插件帮助"

    async def blacklist(self, request):
        data = request.getFirstTextSplit()
        bot = request.bot
        groupid = request.getGroupId()
        cookie = getCookie(groupid, "blackList")
        if cookie is None:
            cookie = []
        if "list" in data:
            await request.sendMessage(MessageChain().text(str(cookie)))
            return
        if len(data) < 3:
            await request.sendMessage(MessageChain().text("/blacklist [add/remove] qq"))
            return
        target = data[2]
        try:
            target = str(int(target))
            if target != data[2] or GetSystemPermissionAndCheck(target, "ADMINISTRATOR"):
                raise
        except Exception as e:
                await request.sendMessage(MessageChain().text("???"))
                return 
        groupMemberList = await bot.memberList(groupid)
        groupMemberList = groupMemberList["data"]
        checkFlag = True
        if GetSystemPermissionAndCheck(request.getSenderId(), "ADMINISTRATOR"):
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
        setCookie(groupid, "blackList", cookie)
        await request.sendMessage(MessageChain().text("完成"))

    def blackListCheck(self, request):
        if request.type == "GroupMessage":
            cookie = getCookie(request.getGroupId(), "blackList")
            if cookie is not None and request.getSenderId() in cookie:
                return False
        return True

def handle(*args, **kwargs):
    return plugin(*args, **kwargs)
