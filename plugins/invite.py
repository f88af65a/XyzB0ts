from botsdk.util.BotPlugin import BotPlugin
from botsdk.util.Permission import roleCheck


class plugin(BotPlugin):
    "/hello"

    def onLoad(self):
        self.name = "invite"
        self.addBotType("Mirai")
        self.addType("BotInvitedJoinGroupRequestEvent", self.groupInvite)
        self.addType("NewFriendRequestEvent", self.friendRequest)
        self.canDetach = True

    async def groupInvite(self, request):
        await request.getBot().BotInvitedJoinGroupRequestEvent(
            {
                "eventId": request["eventId"],
                "fromId": request["fromId"],
                "groupId": request["groupId"],
                "operate":
                    (0 if await roleCheck(request, {"Inviter"}) else 1),
                "message": ""
            }
        )

    async def friendRequest(self, request):
        await request.getBot().NewFriendRequestEvent(
            {
                "eventId": request["eventId"],
                "fromId": request["fromId"],
                "groupId": request["groupId"],
                "operate":
                    (0 if await roleCheck(request, {"Inviter"}) else 1),
                "message": ""
            }
        )


def handle(*args, **kwargs):
    return plugin(*args, **kwargs)
