import time
import json
import botsdk.Bot
import botsdk.BotRequest
import random
import os
import base64
import math
from PIL import Image
from botsdk.tool.MessageChain import MessageChain
from botsdk.tool.BotPlugin import BotPlugin
from botsdk.tool.Cookie import *
from botsdk.tool.HttpRequest import *
from botsdk.tool.JsonConfig import config
from botsdk.tool.TimeTest import *
from botsdk.tool.Error import debugPrint

class plugin(BotPlugin):
    def __init__(self):
        super().__init__()
        self.listenType = []
        #[["type1",func],["type2",func],...,["typen",func]]
        self.listenTarget = [["GroupMessage", "pixiv.search", self.search],
                              ["GroupMessage", "pixiv.rank", self.rank]]
        #[["type1","target",func],["type2","target",func],...,["typen","target",func]]
        self.name = "pixiv"
        #"插件名称"
        self.info = "p站相关"
        #"插件信息"
        self.help = "/pixiv.[search/rank] [关键字/无] [on]"
        #"插件帮助"
        self.permissionSet = {"OWNER","ADMINISTRATOR","MEMBER"}
        self.url = getConfig()["hibiapiUrl"]
        self.canDetach = True
        self.limitTags = {"R18","R-18","R18G","R-18G","R18-G"}

    async def search(self, request):
        bot = request.bot
        groupid = request.groupId
        data = request.getFirstTextSplit()
        if len(data) < 2:
            await bot.sendGroupMessage(request.groupId, MessageChain().text("/pixiv.search 关键字").getData())
            return
        response = []
        #startMark = random.randint(1,30)
        startMark = 1
        randomMark = startMark
        useMark = set()
        useMark.add(randomMark)
        randomCount = 0
        usersOn = ""
        if "on" in data:
            usersOn = " users入り"
        markList = [i for i in range(1,102)]
        while len(markList) > 0 and len(response) < 150:
            searchMark = markList[random.randint(0, len(markList) - 1)]
            url = self.url + f"/api/pixiv/search?word={data[1]}{usersOn}&page={searchMark}&size=50"
            searchData = json.loads(await get(url))
            if "illusts" not in searchData or len(searchData["illusts"]) == 0:
                del markList[markList.index(searchMark):]
                continue
            markList.remove(searchMark)
            for j in searchData["illusts"]:
                safeFlag = True
                for k in j["tags"]:
                    if k["name"] in self.limitTags:
                        safeFlag = False
                        break
                if safeFlag:
                    response += [j]
        if len(response) == 0:
            await bot.sendGroupMessage(request.groupId, MessageChain().text("没有图捏").getData())
            return
        await self.getImgFromList(data, response, request)

    async def rank(self, request):
        bot = request.bot
        groupid = request.groupId
        rankType=["day","week","month","rookie","original","male"]
        url = f'''{self.url}/api/pixiv/rank?RankingType={rankType[random.randint(0,len(rankType) - 1)]}&date={time.strftime("%Y-%m-%d", time.localtime(time.time() - random.randint(1,14) * (60 * 60 * 24)))}'''
        response = json.loads(await get(url))["illusts"]
        await self.getImgFromList(["on"], response, request)

    async def getImgFromList(self, data, response, request):
        re = None
        if "on" in data:
            re = response[random.randint(0, len(response) - 1)]
        else:
            response.sort(key=lambda i : i["total_view"] + i["total_bookmarks"] * 20, reverse = True)
            re = response[random.randint(0, max(math.floor(len(response) * 0.5), 1))]
        msg = MessageChain().text(f'''搜索到{len(response)}个作品\n作者:{re["user"]["name"]}\n标题:{re["title"]}\n链接:www.pixiv.net/artworks/{re["id"]}\nVIEW:{re["total_view"]}\nLIKE:{re["total_bookmarks"]}''')
        imgType = None
        if False and "full" in data and "meta_single_page" in re and "original_image_url" in re["meta_single_page"]:
            imgType = re["meta_single_page"]["original_image_url"]
        elif "original" in re["image_urls"]:
            imgType = re["image_urls"]["original"]
        elif "large" in re["image_urls"]:
            imgType = re["image_urls"]["large"]
        elif "medium" in re["image_urls"]:
            imgType = re["image_urls"]["medium"]
        elif "square_medium" in re["image_urls"]:
            imgType = re["image_urls"]["square_medium"]
        if imgType is None:
            await request.sendMessage(msg)
        imgType = imgType.replace("https","http")
        imgType = imgType.replace("i.pximg.net","45.148.120.239:8084")
        img = await get(imgType.replace("https","http"), headers={"user-agent":"Mozilla/5.0 (Windows NT 11.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36", 'Referer': 'https://www.pixiv.net/'}, byte = True)
        #img = await get(imgType.replace("https","http"), headers={"user-agent":"Mozilla/5.0 (Windows NT 11.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36", 'Referer': 'https://www.pixiv.net/'}, proxy="http://45.148.120.239:8084", byte = True)
        if img is not None:
            fPath = config["localFilePath"] + str(re["id"]) + str(random.randint(0,65535)) + ".jpg"
            f = open(fPath, "bw")
            f.write(img)
            f.close()
            image = Image.open(fPath)
            image = image.convert("RGB")
            image.save(fPath)
            msg.text("\n").image(path=config["runPath"] + fPath[2:])
            await request.sendMessage(msg)
            os.remove(fPath)
        else:
            await request.sendMessage(msg)



def handle(*args, **kwargs):
    return plugin(*args, **kwargs)
