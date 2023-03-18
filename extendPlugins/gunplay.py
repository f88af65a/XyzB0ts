import random
from botsdk.util.BotPlugin import BotPlugin


class plugin(BotPlugin):
    def onLoad(self):
        self.addBotType("Mirai")
        self.addBotType("Kaiheila")
        self.name = "gunPlay"
        self.addTarget("GroupMessage", "开枪", self.shot)
        self.addTarget("GROUP:9", "开枪", self.shot)
        self.dead = [
            "你倒在了血泊之中"
        ]
        self.survival = [
            "你躲开了子弹，令人惊叹",
            "居然能用双手夹住子弹！",
            "好像有一股神秘力量帮助你，让子弹静止在你面前并掉落在地上",
            "子弹没有划伤你的光头",
            "美式居合似乎对你没有作用",
            "子弹只擦过了你的衣角",
            "腿只是装饰，上面的大人物是不会懂的",
            "子弹在你身边呼啸而过，但是你依然安然无恙",
            "子弹都无法跟上你的移动",
            "你的防御技巧令人惊叹",
            "这对你来说根本不算什么",
            "就这?"
        ]
        self.ammo = 6

    async def shot(self, request):
        '''开一枪'''
        msg = ""
        if random.randint(0, 6) <= self.ammo:
            msg = self.dead[random.randint(0, len(self.dead) - 1)]
            self.ammo = max(2, self.ammo - 1)
        else:
            msg = self.survival[random.randint(0, len(self.survival) - 1)]
            self.ammo = 6
        await request.send(msg)


def handle(*args, **kwargs):
    return plugin(*args, **kwargs)
