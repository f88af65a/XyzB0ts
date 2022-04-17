from botsdk.util.BotPlugin import BotPlugin


class plugin(BotPlugin):
    def onLoad(self):
        self.addBotType("Mirai")
        self.name = "groupgroup"
        self.addTarget("GroupMessage", "group.say", self.say)
        self.addTarget("GroupMessage", "group", self.group)
        self.canDetach = True

    async def sendToAllGroup(self, request, msg):
        group = request.getCookie("group", id="group")
        if group is None:
            group = {}
        for i in group:
            if request.getId() in group[i]:
                for j in group[i]:
                    if j != request.getId():
                        await request.getBot().sendGroupMessage(
                            j.split(":")[-1],
                            request.makeMessageChain()
                            .text(msg).getData()
                            )

    async def group(self, request):
        '''group add/del 组名'''
        data = request.getFirstTextSplit()
        if len(data) != 3:
            await request.sendMessage(self.group.__doc__)
            return
        cookie = request.getCookie("group", id="group")
        if cookie is None:
            cookie = {}
        if data[1] == "add":
            if data[2] not in cookie:
                cookie[data[2]] = []
            if request.getId() not in cookie[data[2]]:
                cookie[data[2]].append(request.getId())
                request.setCookie("group", cookie, id="group")
        elif data[1] == "del":
            if request.getId() in cookie[data[2]]:
                cookie[data[2]].remove(request.getId())
                request.setCookie("group", cookie, id="group")
            if len(cookie[data[2]]) == 0:
                del cookie[data[2]]
                request.setCookie("group", cookie, id="group")
        else:
            await request.sendMessage("?")
            return
        await request.sendMessage("修改完成")

    async def say(self, request):
        '''group.say 消息'''
        data = request.getFirstTextSplit()
        if len(data) != 2:
            await request.sendMessage(self.recall.__doc__)
            return
        await self.sendToAllGroup(
            request,
            (f'''{request["sender"]["memberName"]}'''
             f'''#{request["sender"]["id"]}\n{data[1]}''')
             )


def handle(*args, **kwargs):
    return plugin(*args, **kwargs)
