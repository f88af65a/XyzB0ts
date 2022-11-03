import dns.resolver
from botsdk.util.BotPlugin import BotPlugin


class plugin(BotPlugin):
    def onLoad(self):
        self.name = "dns"
        self.addTarget("GroupMessage", "dns", self.dns)
        self.addBotType("Mirai")
        self.addBotType("Kaiheila")
        self.canDetach = True
        self.api = "http://ip-api.com/json/{}"

    async def dns(self, request):
        '''dns [domain]
        -d [dns服务器]
        -t [记录类型]
        '''
        requestData = request.getFirstTextSplit()
        if len(requestData) == 1:
            await request.sendMessage(self.getIpInfo.__doc__)
            return
        dnsRequestData = {
            "domain": requestData[1],
            "d": ["223.5.5.5", "1.1.1.1", "8.8.8.8"],
            "t": "A"
        }
        for i in range(2, len(requestData)):
            if (len(requestData[i]) > 1
                    and requestData[i][0] == "-"
                    and i + 1 < len(requestData)):
                key = requestData[i][1:]
                if key == "d":
                    dnsRequestData["d"] = requestData[i+1].split(",")
                elif key == "t":
                    dnsRequestData["t"] = requestData[i+1]
        try:
            resolver = dns.resolver.Resolver()
            resolver.nameservers = dnsRequestData["d"]
            response = resolver.resolve(
                    dnsRequestData["domain"], dnsRequestData["t"])
            responsePrint = ""
            for i in response.response.answer:
                responseSize = len(i.items)
                for j in i.items:
                    responsePrint += j.to_text()
                    responseSize -= 1
                    if responseSize != 0:
                        responsePrint += "\n"
        except Exception as e:
            await request.sendMessage(str(e))
            return
        await request.sendMessage(responsePrint)



def handle(*args, **kwargs):
    return plugin(*args, **kwargs)
