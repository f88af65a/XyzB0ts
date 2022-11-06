from .Cookie import getCookie, AsyncGetCookie


class NotifyTreeNode:
    def __init__(self, notifyName: str = ""):
        self.notifyName = notifyName
        self.nextNode = dict()
        self.notifySet = set()

    def getName(self):
        return self.notifyName

    def getNext(self, name):
        if name not in self.nextNode:
            return None
        return self.nextNode[name]

    def getNotifySet(self):
        return self.notifySet

    def addNode(self, newNode):
        self.nextNode[newNode.getName()] = newNode

    def addNotify(self, groupid: str):
        self.notifySet.add(groupid)

    def removeNotify(self, id: str):
        if id in self.notifySet:
            self.notifySet.remove(id)


class NotifyTree:
    def __init__(self):
        self.root = NotifyTreeNode()

    def add(self, id: str, notifyName: str):
        notifyName = notifyName.split(".")
        if len(notifyName) == 0 or notifyName[0] == "":
            return None
        node = self.root
        for i in range(0, len(notifyName)):
            if (re := node.getNext(notifyName[i])) is not None:
                node = re
                continue
            newNode = NotifyTreeNode(notifyName[i])
            node.addNode(newNode)
            node = newNode
        node.addNotify(id)

    def remove(self, id: str, notifyName: str):
        notifyName = notifyName.split(".")
        if len(notifyName) == 0 or notifyName[0] == "":
            return
        node = self.root
        for i in range(0, len(notifyName)):
            if (re := node.getNext(notifyName[i])) is not None:
                node = re
                continue
            return
        node.removeNotify(id)

    def get(self, notifyName: str):
        notifyName = notifyName.split(".")
        notifySet = set()
        if len(notifyName) == 0 or notifyName[0] == "":
            return NotifyTree
        node = self.root
        for i in range(0, len(notifyName)):
            if (re := node.getNext(notifyName[i])) is not None:
                node = re
                notifySet |= node.getNotifySet()
                continue
            break
        return notifySet


class BotNotifyModule:
    def __init__(self):
        self.notifyTree = NotifyTree()

    def addListen(self, id: str, notifyName: str):
        self.notifyTree.add(id, notifyName)

    def removeListen(self, id: str, notifyName: str):
        self.notifyTree.remove(id, notifyName)

    def notify(self, notifyName: str):
        notifyDict = getCookie("System:Notify", "NotifyList")
        if notifyDict is None or notifyName not in notifyDict:
            return []
        return notifyDict[notifyName]

    async def AsyncNotify(self, notifyName: str):
        notifyDict = await AsyncGetCookie(
                "System:Notify", "NotifyList")
        if notifyDict is None or notifyName not in notifyDict:
            return []
        return notifyDict[notifyName]


notifyModule = BotNotifyModule()


def getNotifyModule():
    return notifyModule


def GetNotifyList(notifyName):
    return getNotifyModule().notify(notifyName)


async def AsyncGetNotifyList(notifyName):
    return await getNotifyModule().AsyncNotify(notifyName)
