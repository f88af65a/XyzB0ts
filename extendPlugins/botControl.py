from botsdk.util.BotPlugin import BotPlugin


class plugin(BotPlugin):
    def onLoad(self):
        self.name = "botControl"
        self.addTarget("GroupMessage", "quitGroup", self.quitGroup)
        self.addTarget("GroupMessage", "listGroup", self.listGroup)
        self.addTarget("GroupMessage", "listFriend", self.listFriend)
        self.addBotType("Mirai")

    async def quitGroup(self, request):
        '''quitGroup q群 #退出q群'''
        ret = await request.getBot().quit(request.getFirstTextSplit()[1])
        await request.sendMessage(f"退出完成 响应{ret}")

    async def listGroup(self, request):
        '''listGroup #打印所有群聊'''
        ret = await request.getBot().groupList()
        if ret["code"] != 0:
            request.sendMessage("请求失败")
            return
        ret = ret["data"]
        data = ""
        for i in range(len(ret)):
            data += (f'''群号:{ret[i]["id"]}\n'''
                     f'''群名:{ret[i]["name"]}\n'''
                     f'''权限:{ret[i]["permission"]}''')
            if i != len(ret) - 1:
                data += "\n------\n"
        await request.sendMessage(data)

    async def listFriend(self, request):
        '''listFriend #打印所有好友'''
        ret = await request.getBot().friendList()
        if ret["code"] != 0:
            request.sendMessage("请求失败")
            return
        ret = ret["data"]
        data = ""
        for i in range(len(ret)):
            data += (f'''Q号:{ret[i]["id"]}\n'''
                     f'''名称:{ret[i]["nickname"]}\n'''
                     f'''备注:{ret[i]["remark"]}''')
            if i != len(ret) - 1:
                data += "\n------\n"
        await request.sendMessage(data)


def handle(*args, **kwargs):
    return plugin(*args, **kwargs)
