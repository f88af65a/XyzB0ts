import random
from botsdk.util.BotPlugin import BotPlugin
import asyncio
import time


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
        self.addTarget("GroupMessage", "转盘", self.zhuanpan)
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
            "就这?",
        ]
        self.ammo = 6
        self.ammo_lock = asyncio.Lock()
        self.zhuanpan_data = {}
        self.zhuanpan_lock = asyncio.Lock()

    async def GetAmmo(self):
        async with self.ammo_lock:
            return self.ammo

    async def SetAmmo(self, ammo):
        async with self.ammo_lock:
            self.ammo = ammo

    async def shot(self, request):
        '''开一枪'''
        msg = ""
        ammo_size = await self.GetAmmo()
        random_size = random.randint(1, 6)
        if random_size > ammo_size:
            msg = self.survival[random.randint(0, len(self.survival) - 1)]
        else:
            msg = self.dead[random.randint(0, len(self.dead) - 1)]
        await self.SetAmmo(max(0, await self.GetAmmo() - 1))
        if await self.GetAmmo() == 0:
            await self.SetAmmo(random.randint(5, 6))
        await request.send(msg)

    async def up_ammo(self, request):
        '''上子弹 [子弹数量]'''
        data = request.getFirstTextSplit()
        if len(data) == 1:
            await request.sendMessage(self.up_ammo.__doc__)
            return
        try:
            ammo_size = int(data[1])
            if ammo_size < 0:
                await request.send("你有那个大病？")
                return
            if ammo_size > 6:
                await request.send("赛博左轮只能上六发，美式转盘适合你")
                return
            await self.SetAmmo(ammo_size)
        except Exception:
            await request.send("数学老师没教你数数？")
            return

    async def CreateNewGame(self, group_id):
        async with self.zhuanpan_lock:
            if group_id not in self.zhuanpan_data:
                self.zhuanpan_data[group_id] = {
                    "member": [],
                    "canjoin": True
                }
                return True
            return False

    async def GetAnStopGame(self, group_id):
        async with self.zhuanpan_lock:
            if group_id in self.zhuanpan_data:
                self.zhuanpan_data[group_id]["canjoin"] = False
                return self.zhuanpan_data[group_id]
            raise "啊？"

    async def DeleteGame(self, group_id):
        async with self.zhuanpan_lock:
            if group_id in self.zhuanpan_data:
                del self.zhuanpan_data[group_id]

    async def CheckAndAddMember(self, group_id, name):
        async with self.zhuanpan_lock:
            if group_id not in self.zhuanpan_data:
                return 0
            if name in self.zhuanpan_data[group_id]["member"]:
                return 1
            if not self.zhuanpan_data[group_id]["canjoin"]:
                return 2
            self.zhuanpan_data[group_id]["member"].append(name)
            return 3

    async def GetZhuanPanMember(self):
        async with self.zhuanpan_lock:
            return self.zhuanpan_member

    async def ClearZhuanPanMember(self, group_id):
        async with self.zhuanpan_lock:
            self.zhuanpan_member.clear()

    async def GameFunction(self, request, group_id):
        try:
            await request.send("转盘游戏开始了,输入 /转盘 加入")
            await asyncio.sleep(30)
            game_data = await self.GetAnStopGame(group_id)
            members = game_data["member"]
            ammo_size = min(len(members), 6)
            for i in range(len(members) - 1):
                local_name = members[i]
                mark = random.randint(i + 1, len(members) - 1)
                members[i] = members[mark]
                members[mark] = local_name
            await request.send(f"本次游戏共有{ammo_size}颗子弹和{len(members)}个参与者")
            await asyncio.sleep(5)
            for i in range(ammo_size):
                msg = ""
                name = members[i]
                r = random.randint(1, 10)
                if r <= 6:
                    msg = f"子弹命中了{name},命中好啊"
                else:
                    msg = f"马了一枪,{name}差点寄了"
                await request.send(msg)
                await asyncio.sleep(5)
            await request.send("转盘游戏结束了")
        except Exception:
            pass
        await self.DeleteGame(group_id)

    async def zhuanpan(self, request):
        group_id = request.getGroupId()
        sender_name = request["sender"]["memberName"]
        if await self.CreateNewGame(group_id):
            await self.CheckAndAddMember(group_id, sender_name)
            asyncio.ensure_future(
                self.GameFunction(request, group_id)
            )
        else:
            add_state = await self.CheckAndAddMember(group_id, sender_name)
            if add_state == 3:
                await request.send(f"{sender_name}加入了转盘游戏")
                return
            elif add_state == 0:
                await request.send("加入失败")
            elif add_state == 1:
                await request.send("不能重复加入")
            else:
                await request.send("游戏未结束")


def handle(*args, **kwargs):
    return plugin(*args, **kwargs)
