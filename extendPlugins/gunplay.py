import random
from botsdk.util.BotPlugin import BotPlugin
import asyncio
import time
import traceback


class DuiQiangGame:
    DEFAULT_DMG = 5
    DEFAULT_BULLETS = 1
    DEFAULT_MIN_DMG_MULTI = 1
    DEFAULT_MAX_DMG_MULTI = 5

    def __init__(self, request, members, add_log, sleep_time=5):
        self.request = request
        self.members = members
        self.member_data = {
            i: {
                "name": i,
                "hp": 100,
                "dmg": DuiQiangGame.DEFAULT_DMG,
                "location": 8,
                "range": 2,
                "buffer": [],
                "items": [],
                "bullets": DuiQiangGame.DEFAULT_BULLETS,
                "min_dmg_multi": DuiQiangGame.DEFAULT_MIN_DMG_MULTI,
                "max_dmg_multi": DuiQiangGame.DEFAULT_MAX_DMG_MULTI,
                "armor": 0,
                "action": 0
            } for i in members
        }
        for i in self.members:
            self.member_data[i]["location"] = random.randint(0, 15)
        self.items = [
            "flashbomb",
            "grenade",
            "smoke"
        ]
        self.round = 0
        self.round_msg = []
        self.AddLog = add_log
        self.kill_log = []
        self.sleep_time = sleep_time

    def AddRoundMessage(self, msg):
        self.round_msg.append(msg)

    async def SendRoundMessage(self):
        await self.request.send(
            "\n".join(self.round_msg)
        )
        self.round_msg.clear()

    def GetDistanceByName(self, p1, p2):
        return abs(
            self.member_data[p1]["location"] -
            self.member_data[p2]["location"]
        )

    def GetRandomPlayer(self):
        return self.member_data[
            self.members[random.randint(0, len(self.members) - 1)]
        ]

    def RandomMembers(self):
        for i in range(len(self.members) - 1):
            mark = random.randint(i + 1, len(self.members) - 1)
            local_name = self.members[i]
            self.members[i] = self.members[mark]
            self.members[mark] = local_name

    def GetLowActionPlayer(self):
        action_player_list = [
            (i, self.member_data[i]["action"]) for i in self.members
        ]
        action_player_list.sort(key=lambda x: x[1])
        ret_member_name = action_player_list[
            random.randint(0, min(len(action_player_list) - 1, 4))
        ][0]
        return self.member_data[ret_member_name]

    def SetAction(self, member, action):
        member["action"] = action

    def GetRandomPlayerReject(self, member):
        member_list = [i for i in self.members]
        member_list.remove(member["name"])
        if len(member_list) == 0:
            return None
        return self.member_data[
            member_list[random.randint(0, len(member_list) - 1)]
        ]

    def GetNearestPlayer(self, member):
        member_list = [i for i in self.members]
        member_list.remove(member["name"])
        if len(member_list) == 0:
            return None
        member_list = [
            (i, self.GetDistanceByName(member["name"], i))
            for i in member_list
        ]
        member_list.sort(key=lambda x: x[1])
        return self.member_data[
            member_list[
                random.randint(0, min(member["range"], len(member_list) - 1))
            ][0]
        ]

    def GetRandomPlayerByLocation(
            self, member, target_member, radius):
        member_list = [i for i in self.members]
        member_list.remove(member["name"])
        if len(member_list) == 0:
            return None
        origin_location = target_member["location"]
        ret_member_list = []
        for i in member_list:
            location = self.member_data[i]["location"]
            if (location >= origin_location - radius
                    and location <= origin_location + radius):
                ret_member_list.append(i)
        return self.member_data[
            ret_member_list[random.randint(0, len(ret_member_list) - 1)]
        ]

    def GiveDamageInfo(
            self, member, target_member, damage, origin_damage):
        old_hp = target_member["hp"]
        target_member["hp"] -= damage
        if origin_damage is None:
            origin_damage = damage
        return (
            f'{member["name"]}({member["hp"]})给了{target_member["name"]}'
            f'({old_hp} -> {target_member["hp"]})一枪{origin_damage}血'
        )

    def MidRoundMessage(self):
        if self.round % 10 == 0 and self.round >= 0:
            self.AddRoundMessage(
                f"当前在场{len(self.members)}人"
            )
            for i in self.members:
                self.AddRoundMessage(
                    f'{i}({self.member_data[i]["hp"]})'
                )
            return True
        return False

    def IsLive(self, member):
        return member["hp"] > 0

    async def Kill(self, member, target):
        if member["name"] != target["name"]:
            await self.AddLog(
                self.request,
                member["name"],
                "k", 1
            )
        await self.AddLog(
            self.request,
            target["name"],
            "d", 1
        )
        self.members.remove(target["name"])
        self.kill_log.append(
            f'{member["name"]} -> {target["name"]}'
        )

    def AddBuffer(self, member, buff_type, end):
        member["buffer"].append(
            {
                "type": buff_type,
                "end": end
            }
        )

    def CheckBuffer(self, member):
        buffer_mark = 0
        can_action_flag = True
        while buffer_mark < len(member["buffer"]):
            buffer = member["buffer"][buffer_mark]
            if buffer["end"] < self.round:
                del member["buffer"][buffer_mark]
                continue
            if buffer["type"] == "flash" and can_action_flag:
                if buffer["end"] >= self.round:
                    self.AddRoundMessage(
                        f'{member["name"]}被白了无法行动'
                    )
                    can_action_flag = False
            buffer_mark += 1
        return can_action_flag

    def HasBuffer(self, member, buff_type):
        buffer_mark = 0
        while buffer_mark < len(member["buffer"]):
            if member["buffer"][buffer_mark]["end"] < self.round:
                del member["buffer"][buffer_mark]
                continue
            buffer_mark += 1
        for i in member["buffer"]:
            if i["type"] == buff_type:
                return True
        return False

    def RewardRound(self, member):
        if random.randint(1, 100) <= 50:
            move_distance = 6
            location = member["location"]
            left = max(0, location - move_distance)
            right = min(15, location + move_distance)
            new_location = random.randint(left, right)
            member["location"] = new_location
            self.AddRoundMessage(
                f'{member["name"]}({member["hp"]})改善了战术位置'
            )
        action_point = random.randint(1, 100)
        if action_point <= 35:
            if member["hp"] < 100:
                old_hp = member["hp"]
                member["hp"] += 5 * random.randint(1, 10)
                member["hp"] = min(
                    member["hp"],
                    100
                )
                self.AddRoundMessage(
                    f'{member["name"]}({old_hp} -> {member["hp"]})选择了打血'
                )
            else:
                self.AddRoundMessage(
                    f'{member["name"]}({member["hp"]})打血的时候发现血是满的'
                )
        elif action_point <= 70:
            weapon = random.randint(1, 100)
            if weapon <= 35:
                member["dmg"] += random.randint(5, 20)
            elif weapon <= 70:
                member["bullets"] += random.randint(1, 5)
            elif weapon <= 100:
                rand_multi = random.randint(1, 3)
                member["min_dmg_multi"] += rand_multi
                member["max_dmg_multi"] += rand_multi
            self.AddRoundMessage(
                f'{member["name"]}({member["hp"]})选择了起枪'
            )
        elif action_point <= 100:
            member["range"] += 1
            self.AddRoundMessage(
                f'{member["name"]}({member["hp"]})装了个镜子'
            )
        if random.randint(1, 100) <= 35:
            self.AddBuffer(member, "camper", self.round+2)
            self.AddRoundMessage(
                f'{member["name"]}({member["hp"]})开蹲'
            )

    def AddItem(self, member, item):
        member["items"].append(item)

    def RemoveItem(self, member, item):
        member["items"].remove(item)

    def HasItem(self, member):
        return len(member["items"]) > 0

    async def UseItem(self, member):
        item = member["items"][
            random.randint(0, len(member["items"]) - 1)
        ]
        target_member = self.GetRandomPlayerReject(member)
        if target_member is None:
            return
        if item == "flashbomb":
            location = target_member["location"]
            flash_list = []
            for i in self.members:
                p = self.member_data[i]
                if abs(p["location"] - location) <= 2:
                    flash_list.append(i)
                    self.AddBuffer(
                        p,
                        "flash",
                        self.round + 3
                    )
            self.AddRoundMessage(
                f'{member["name"]}朝{target_member["name"]}丢了一颗闪，闪到了'
            )
            self.AddRoundMessage(
                "\n".join(flash_list)
            )
            self.AddRoundMessage(
                "这些人三回合内无法行动"
            )
        elif item == "grenade":
            location = target_member["location"]
            location = (
                target_member["location"]
                + (
                    (-1 if (random.randint(0, 1) == 0) else 1)
                    if (random.randint(0, 1) == 0) else 0
                )
            )
            location = max(location, 0)
            location = min(location, 15)
            aoe_dmg = [60, 40, 20, 10]
            bomb_list = []
            dead_list = []
            for i in self.members:
                p = self.member_data[i]
                distance = abs(p["location"] - location)
                if distance <= 3:
                    old_hp = p["hp"]
                    p["hp"] -= aoe_dmg[distance]
                    bomb_list.append(f'{i}({old_hp} -> {p["hp"]})')
                    if not self.IsLive(p):
                        dead_list.append(i)
            for i in dead_list:
                p = self.member_data[i]
                await self.Kill(member, p)
            self.AddRoundMessage(
                f'{member["name"]}朝{target_member["name"]}丢了一颗雷，炸到了'
            )
            self.AddRoundMessage(
                "\n".join(bomb_list)
            )
            if len(dead_list):
                self.AddRoundMessage(
                     "这些人寄了"
                )
                self.AddRoundMessage(
                     "\n".join(dead_list)
                )
        elif item == "smoke":
            location = member["location"]
            smoke_list = []
            for i in self.members:
                p = self.member_data[i]
                smoke_distance = abs(p["location"] - location)
                if smoke_distance <= 2:
                    smoke_list.append(p)
            for i in smoke_list:
                self.AddBuffer(
                    p,
                    "smoke",
                    self.round+5
                )
            self.AddRoundMessage(
                f'{member["name"]}脚下生烟,这些人被烟雾笼罩,受到的伤害减半'
            )
            self.AddRoundMessage(
                "\n".join([i["name"] for i in smoke_list])
            )
        self.RemoveItem(member, item)

    async def Shot(self, member, target_member):
        dmg = member["dmg"]
        distance = abs(target_member["location"] - member["location"])
        acc = 90
        if distance < member["range"]:
            for _ in range(member["range"] - distance):
                dmg *= 0.85
                acc *= 0.95
        if self.HasBuffer(target_member, "smoke"):
            dmg *= 0.5
        dmg = int(dmg)
        hit_dmg = dmg * random.randint(
            member["min_dmg_multi"],
            member["max_dmg_multi"]
        ) + int(self.round/2)
        if hit_dmg >= 80:
            self.AddRoundMessage(
                "时间差不多咯"
            )
        hit = True
        origin_hit_dmg = hit_dmg
        if random.randint(1, 100) > int(acc):
            hit = False
            hit_dmg = 0
        armor_dmg = 0
        if hit and hit_dmg > 0 and target_member["armor"] > 0:
            armor_dmg = min(hit_dmg, target_member["armor"])
            target_member["armor"] -= armor_dmg
            hit_dmg -= armor_dmg
        self.AddRoundMessage(
            self.GiveDamageInfo(
                member, target_member,
                hit_dmg, origin_hit_dmg
            )
        )
        if armor_dmg > 0:
            self.AddRoundMessage(
                f'{target_member["name"]}的护甲扛了{armor_dmg}伤'
            )
        if not hit:
            self.AddRoundMessage("马了,马了好啊")

    async def ShotRound(self, member, target_member=None, deep=0):
        action_point = random.randint(1, 100)
        if target_member is None:
            if action_point <= 50:
                target_member = self.GetRandomPlayerReject(member)
            elif action_point <= 100:
                target_member = self.GetNearestPlayer(member)
        if target_member is None:
            self.AddRoundMessage("你别说，没找到人,嘿嘿")
            return
        self.AddRoundMessage(
            f'{member["name"]}瞄准了{target_member["name"]}'
        )
        if member["bullets"] >= 4:
            self.AddRoundMessage(
                "午食已倒"
            )
        for _ in range(member["bullets"]):
            target_member_random = self.GetRandomPlayerByLocation(
                member, target_member, 1
            )
            await self.Shot(member, target_member_random)
            if not self.IsLive(target_member_random):
                await self.Kill(member, target_member_random)
                self.AddRoundMessage(
                    f'{target_member_random["name"]}寄了'
                )
                break
        member["dmg"] = DuiQiangGame.DEFAULT_DMG
        member["bullets"] = DuiQiangGame.DEFAULT_BULLETS
        member["min_dmg_multi"] = DuiQiangGame.DEFAULT_MIN_DMG_MULTI
        member["max_dmg_multi"] = DuiQiangGame.DEFAULT_MAX_DMG_MULTI
        if (self.IsLive(target_member)
                and self.HasBuffer(target_member, "camper")
                and deep == 0):
            self.AddRoundMessage(f'{target_member["name"]}蹲到了')
            await self.ShotRound(target_member, member, 1)

    def RandomGiveItem(self, member):
        if random.randint(1, 100) <= 15:
            item_r = random.randint(1, 100)
            item = None
            if item_r <= 30:
                item = "flashbomb"
            elif item_r <= 60:
                item = "smoke"
            elif item_r <= 100:
                item = "grenade"
            self.AddItem(
                member,
                item
            )
            self.AddRoundMessage(
                f'{member["name"]}顺手捡了个{item}'
            )

    async def AttackRound(self, member):
        if self.HasItem(member):
            await self.UseItem(member)
        if self.IsLive(member):
            await self.ShotRound(member)
            self.RandomGiveItem(member)

    async def GameLoop(self):
        random.seed(int(time.time()))
        while len(self.members) > 1:
            try:
                if self.MidRoundMessage():
                    self.round += 1
                    await self.SendRoundMessage()
                    await asyncio.sleep(self.sleep_time)
                    continue
                if random.randint(0, 1):
                    action_player = self.GetLowActionPlayer()
                else:
                    action_player = self.GetRandomPlayer()
                if not self.CheckBuffer(action_player):
                    self.SetAction(action_player, self.round)
                    await self.SendRoundMessage()
                    self.RandomMembers()
                    self.round += 1
                    await asyncio.sleep(self.sleep_time)
                    continue
                r = random.randint(1, 100)
                if r <= 40:
                    self.RewardRound(action_player)
                elif r <= 100:
                    await self.AttackRound(action_player)
                self.SetAction(action_player, self.round)
                await self.SendRoundMessage()
                self.RandomMembers()
                self.round += 1
            except Exception:
                print(traceback.format_exc())
            await asyncio.sleep(self.sleep_time)
        winner = None
        if len(self.members) != 0:
            winner = self.members[0]
        return winner, self.kill_log


class plugin(BotPlugin):
    def onLoad(self):
        self.addBotType("Mirai")
        self.addBotType("Kaiheila")
        self.name = "gunPlay"
        self.addTarget("GroupMessage", "开枪", self.shot)
        self.addTarget("GROUP:9", "开枪", self.shot)
        self.addTarget("GroupMessage", "转盘", self.zhuanpan)
        self.addTarget("GroupMessage", "对枪", self.duiqiang)
        self.addTarget("GroupMessage", "记录", self.zhuanpanlog)
        self.addTarget("GroupMessage", "调参", self.setargs)
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
            "就这?",
        ]
        self.ammo = 6
        self.ammo_lock = asyncio.Lock()
        self.zhuanpan_data = {}
        self.zhuanpan_lock = asyncio.Lock()
        self.duiqiang_data = {}
        self.duiqiang_lock = asyncio.Lock()

    async def AddLog(self, request, name, log, size):
        cookie = await request.AsyncGetCookie("gungame")
        if cookie is None:
            cookie = {}
        if name not in cookie:
            cookie[name] = {}
        if log not in cookie[name]:
            cookie[name][log] = 0
        cookie[name][log] += size
        await request.AsyncSetCookie("gungame", cookie)

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
                isDead = True
                if r <= 6:
                    msg = f"子弹命中了{name},命中好啊"
                else:
                    msg = f"马了一枪,{name}差点寄了"
                    isDead = False
                cookie = await request.AsyncGetCookie("gungame")
                if cookie is None:
                    cookie = {}
                if name not in cookie:
                    cookie[name] = {
                        "l": 0,
                        "d": 0
                    }
                if isDead:
                    cookie[name]["d"] += 1
                else:
                    cookie[name]["l"] += 1
                await request.AsyncSetCookie("gungame", cookie)
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

    async def zhuanpanlog(self, request):
        sender_name = request["sender"]["memberName"]
        cookie = await request.AsyncGetCookie("gungame")
        if cookie is None or sender_name not in cookie:
            await request.send("无记录")
            return
        msg = []
        for i in cookie[sender_name]:
            msg.append(f"{i}: {cookie[sender_name][i]}")
        await request.send(
            f'''{sender_name}:\n'''
            + "\n".join(msg)
        )

    async def CreateDuiQiangNewGame(self, group_id):
        async with self.zhuanpan_lock:
            if group_id not in self.zhuanpan_data:
                self.zhuanpan_data[group_id] = {
                    "member": [],
                    "canjoin": True,
                    "startTime": int(time.time() + 30)
                }
                return True
            return False

    async def GetAnStopDuiQiangGame(self, group_id):
        async with self.zhuanpan_lock:
            if group_id in self.zhuanpan_data:
                self.zhuanpan_data[group_id]["canjoin"] = False
                return self.zhuanpan_data[group_id]
            raise "啊？"

    async def DeleteDuiQiangGame(self, group_id):
        async with self.zhuanpan_lock:
            if group_id in self.zhuanpan_data:
                del self.zhuanpan_data[group_id]

    async def CheckAndAddMemberToDuiQiang(self, group_id, name):
        async with self.zhuanpan_lock:
            if group_id not in self.zhuanpan_data:
                return 0
            if name in self.zhuanpan_data[group_id]["member"]:
                return 1
            if not self.zhuanpan_data[group_id]["canjoin"]:
                return 2
            self.zhuanpan_data[group_id]["member"].append(name)
            self.zhuanpan_data[group_id]["startTime"] = max(
                self.zhuanpan_data[group_id]["startTime"],
                int(time.time() + 10)
            )
            return 3

    async def CheckDuiQiangStartTime(self, group_id):
        async with self.zhuanpan_lock:
            return self.zhuanpan_data[group_id]["startTime"]

    async def DuiQiangGameFunction(self, request, group_id):
        try:
            await request.send("对枪游戏开始了,输入 /对枪 加入")
            while True:
                this_time = int(time.time())
                start_time = await self.CheckDuiQiangStartTime(group_id)
                if this_time >= start_time:
                    break
                await asyncio.sleep(start_time - this_time)
            game_data = await self.GetAnStopDuiQiangGame(group_id)
            members = game_data["member"]
            if len(members) <= 1:
                await request.send("兄弟没人啊兄弟，对什么枪")
                raise
            # 初始化一次游戏的数据
            game = DuiQiangGame(request, members, self.AddLog)
            winner, game_log = await game.GameLoop()
        except Exception:
            pass
        try:
            if winner is None:
                end_msg = "对枪游戏结束了 大家都寄了\n" + "\n".join(game_log)
            else:
                await self.AddLog(
                    request, winner, "w", 1
                )
                end_msg = f"对枪游戏结束了 赢家是{winner}\n" + "\n".join(game_log)
            await request.send(end_msg)
        except Exception:
            pass
        await self.DeleteDuiQiangGame(group_id)

    async def duiqiang(self, request):
        group_id = request.getGroupId()
        sender_name = request["sender"]["memberName"]
        if await self.CreateDuiQiangNewGame(group_id):
            await self.CheckAndAddMemberToDuiQiang(group_id, sender_name)
            asyncio.ensure_future(
                self.DuiQiangGameFunction(request, group_id)
            )
        else:
            add_state = await self.CheckAndAddMemberToDuiQiang(
                group_id,
                sender_name
            )
            if add_state == 3:
                await request.send(f"{sender_name}加入了对枪游戏")
                return
            elif add_state == 0:
                await request.send("加入失败")
            elif add_state == 1:
                await request.send("不能重复加入")
            else:
                await request.send("游戏未结束")

    async def setargs(self, request):
        await request.send(
            "参数设置完成"
        )


def handle(*args, **kwargs):
    return plugin(*args, **kwargs)
