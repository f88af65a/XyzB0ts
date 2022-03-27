from botsdk.util.BotPlugin import BotPlugin
from botsdk.util.Permission import permissionCheck


class plugin(BotPlugin):
    "/hello"

    def onLoad(self):
        self.name = "invite"
        self.addBotType("Mirai")
        self.addType("BotInvitedJoinGroupRequestEvent", self.groupInvite)
        self.addType("NewFriendRequestEvent", self.groupInvite)
        self.canDetach = True

    async def groupInvite(self, request):
        request.getBot().BotInvitedJoinGroupRequestEvent(
            eventId=request["eventId"],
            fromId=request["fromId"],
            groupId=request["groupId"],
            operate=(0 if permissionCheck(request, "System:Owner") else 1),
            message=""
        )

    async def friendRequest(self, request):
        request.getBot().NewFriendRequestEvent(
            eventId=request["eventId"],
            fromId=request["fromId"],
            groupId=request["groupId"],
            operate=(0 if permissionCheck(request, "System:Owner") else 1),
            message=""
        )


def handle(*args, **kwargs):
    return plugin(*args, **kwargs)
