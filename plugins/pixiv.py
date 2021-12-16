import json
import math
import os
import random
import time

from botsdk.BotRequest import BotRequest
from botsdk.util.BotPlugin import BotPlugin
from botsdk.util.HttpRequest import get
from botsdk.util.JsonConfig import getConfig
from botsdk.util.MessageChain import MessageChain
from PIL import Image


class plugin(BotPlugin):
    '''p站相关功能\n/pixiv.[search/rank] [关键字/无] [on]'''
    def __init__(self):
        super().__init__()
        self.name = "pixiv"
        self.addTarget("GroupMessage", "pixiv.search", self.search)
        self.addTarget("GroupMessage", "pixiv.rank", self.rank)
        self.permissionSet = {"OWNER", "ADMINISTRATOR", "MEMBER"}
        self.limitTags = {"R18", "R-18", "R18G", "R-18G", "R18-G"}
        self.canDetach = True

    def init(self, bot):
        self.url = self.getConfig()["hibiapiUrl"]
        self.proxy = self.getConfig()["pixivProxy"]

    async def search(self, request: BotRequest):
        data = request.getFirstTextSplit()
        if len(data) < 2:
            request.sendMessage(MessageChain().text("/pixiv.search 关键字"))
            return
        response = []
        startMark = 1
        randomMark = startMark
        useMark = set()
        useMark.add(randomMark)
        usersOn = ""
        if "on" in data:
            usersOn = " users入り"
        markList = [i for i in range(1, 102)]
        while len(markList) > 0 and len(response) < 150:
            searchMark = markList[random.randint(0, len(markList) - 1)]
            url = (self.url + "/api/pixiv/search?word="
                   + f"{data[1]}{usersOn}&page={searchMark}&size=50")
            searchData = await get(url)
            if searchData is None:
                continue
            searchData = json.loads(searchData)
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
            await request.sendMessage(MessageChain().text("没有搜到图或者响应超时"))
            return
        await self.getImgFromList(data, response, request)

    async def rank(self, request: BotRequest):
        rankType = ["day", "week", "month", "rookie", "original", "male"]
        url = (f'''{self.url}/api/pixiv/rank?RankingType='''
               f'''{rankType[random.randint(0,len(rankType) - 1)]}&date='''
               f'''{time.strftime(
                   "%Y-%m-%d", time.localtime(
                       time.time() - random.randint(1,14)
                       * (60 * 60 * 24)))}''')
        response = await get(url)
        if response is None:
            await request.sendMessage(MessageChain().plain("响应超时"))
            return
        response = json.loads(response)["illusts"]
        if len(response) == 0:
            await request.sendMessage(MessageChain().plain("怎么会没有图太怪了"))
            return
        await self.getImgFromList(["on"], response, request)

    async def getImgFromList(self, data, response, request):
        re = None
        if "on" in data:
            re = response[random.randint(0, len(response) - 1)]
        else:
            response.sort(
                key=lambda i: i["total_view"] + i["total_bookmarks"] * 20,
                reverse=True)
            re = response[random.randint(
                0, max(math.floor(len(response) * 0.5), 1))]
        msg = MessageChain().text(
            (f'''搜索到{len(response)}个作品\n作者:{re["user"]["name"]}\n标题:'''
             f'''{re["title"]}\n链接:www.pixiv.net/artworks/{re["id"]}\nVIEW:'''
             f'''{re["total_view"]}\nLIKE:{re["total_bookmarks"]}'''))
        imgType = None
        if (False and "full" in data
                and "meta_single_page" in re
                and "original_image_url" in re["meta_single_page"]):
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
        imgType = imgType.replace("https", "http")
        imgType = imgType.replace("i.pximg.net", self.proxy)
        img = await get(
            imgType.replace("https", "http"),
            headers={"user-agent": (
                    "Mozilla/5.0 (Windows NT 11.0; Win64; x64)"
                    " AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0."
                    "4606.61 Safari/537.36"),
                'Referer': 'https://www.pixiv.net/'},
            byte=True)
        if img is not None and len(img) != 0:
            fPath = (getConfig()["localFilePath"]
                     + str(re["id"])
                     + str(random.randint(0, 65535))
                     + ".jpg")
            f = open(fPath, "bw")
            f.write(img)
            f.close()
            image = Image.open(fPath)
            image = image.convert("RGB")
            image.save(fPath)
            msg.text("\n").image(path=getConfig()["appPath"] + fPath[1:])
            await request.sendMessage(msg)
            os.remove(fPath)
        else:
            await request.sendMessage(msg)


def handle(*args, **kwargs):
    return plugin(*args, **kwargs)
