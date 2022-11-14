import dns.resolver
from botsdk.util.BotPlugin import BotPlugin


class plugin(BotPlugin):
    def onLoad(self):
        self.name = "dns"
        parser = self.addTargetWithArgs("GroupMessage", "dns", self.dns)
        parser.Add("domain", help="需要查询的域名")
        parser.Add(
            "-d", "--dns",
            meta="DNS地址",
            help="修改默认使用的dns地址",
            required=False
        )
        parser.Add(
            "-t", "--target",
            meta="记录类型",
            help="记录类型,默认为A记录",
            required=False
        )
        self.addBotType("Mirai")
        self.addBotType("Kaiheila")
        self.canDetach = True
        self.api = "http://ip-api.com/json/{}"

    async def dns(self, request):
        '''dns [domain]
        -d [dns服务器]
        -t [记录类型]
        '''
        args = request.getArgs()
        dnsRequestData = {
            "domain": args["domain"],
            "d": ["223.5.5.5", "1.1.1.1", "8.8.8.8"],
            "t": "A"
        }
        if "target" in args:
            dnsRequestData["d"] = args["target"].split(",")
        if "dns" in args:
            dnsRequestData["t"] = args["dns"]
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
