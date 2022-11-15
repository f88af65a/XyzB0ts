import ujson as json
from jsonpath import jsonpath

from botsdk.util.BotPlugin import BotPlugin
from botsdk.util.HttpRequest import get
from botsdk.util.JsonConfig import getConfig


class plugin(BotPlugin):
    def onLoad(self):
        self.name = "jr"
        self.addBotType("Mirai")
        self.addTarget("GroupMessage", "System:Owner:define", self.define)
        self.addType("GroupMessage", self.typeHandle)
        self.parseRequest = {}
        self.addParseRequest("get", self.get)
        self.canDetach = True

    def addParseRequest(self, key, func):
        self.parseRequest[key] = func

    def getParseRequest(self, key):
        if key not in self.parseRequest:
            raise Exception(f"{key} 不存在")
        return self.parseRequest[key]

    async def get(self, d, h, domain, port=80, path="/", parameter=""):
        return await get(f"{h}://{domain}:{port}{path}?{parameter}")

    async def parameterParse(self, s: str, d, cache):
        s = s.format_map(d)
        s = s.split(":")
        if len(s) == 0:
            raise Exception("切片失败")
        elif len(s) == 1:
            if s[0] not in d:
                raise Exception(f"{s[0]}不存在")
            return d[s[0]]
        else:
            args = s[1: -1]
            request = s[0]
            jp = s[-1]
            rq = ":".join(s[:-1])
            try:
                if rq in cache:
                    jsonData = cache[rq]
                else:
                    jsonData = json.loads(
                        await self.getParseRequest(request)(d, *args)
                    )
                    cache[rq] = jsonData
                p = jsonpath(jsonData, jp)
                if p is False or len(p) == 0:
                    return "None"
                return str(jsonpath(jsonData, jp)[0])
            except Exception as e:
                return str(e)

    async def parse(self, s: str, d: dict, isStr=True):
        s = s.replace(r"\n", "\n")
        ll, rr, left = 0, 0, 0
        cache = {}
        while True:
            isParsed = False
            for i in range(left, len(s)):
                if s[i] == '{':
                    if ll == 0:
                        left = i
                    ll += 1
                elif s[i] == '}':
                    rr += 1
                if ll == rr and ll != 0:
                    try:
                        parame = await self.parameterParse(
                            s[left + 1: i], d, cache
                        )
                    except Exception as e:
                        parame = str(e)
                    s = (
                        s[:left]
                        + parame
                        + s[i + 1:]
                    )
                    isParsed = True
                    ll, rr, left = 0, 0, left + len(parame) + 1
                    break
            if not isParsed:
                break
        return s

    async def typeHandle(self, request):
        data = request.getFirstTextSplit()
        if data is None:
            return
        if not (len(data) > 0
                and len(data[0]) > 1
                and data[0][0] in getConfig()["commandTarget"]):
            return
        cookie = await request.AsyncGetCookie("define")
        if cookie is None:
            cookie = {}
        target = data[0][1:]
        if target not in cookie:
            return
        retMsg = cookie[target]
        d = {}
        for i in range(1, len(data)):
            d[f"key{i}"] = data[i]
        try:
            retMsg = await self.parse(retMsg, d)
        except Exception as e:
            retMsg = str(e)
        await request.send(retMsg)

    async def define(self, request):
        '''define 关键字 {} #请求'''
        data = request.getFirstTextSplit()
        if len(data) != 3:
            await request.send(self.define.__doc__)
            return
        cookie = await request.AsyncGetCookie("define")
        if cookie is None:
            cookie = {}
        cookie[data[1]] = data[2]
        await request.AsyncSetCookie("define", cookie)
        await request.send("设置完成")
        return


def handle(*args, **kwargs):
    return plugin(*args, **kwargs)
