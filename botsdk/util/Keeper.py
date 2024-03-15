import asyncio


class Node:
    def __init__(self):
        self.data = None
        self.next = dict()

    def GetData(self):
        return self.data

    def SetData(self, data):
        self.data = data

    def GetNext(self, name):
        if name not in self.next:
            return None
        return self.next[name]

    def SetNext(self, name, node):
        self.next[name] = node


class Keeper:
    def __init__(self):
        self.node_tree = Node()
        self.lock = asyncio.Lock()

    def _GetNode(self, path):
        node = self.node_tree
        if path.startswith("/"):
            path = path[1:]
        for p in path.split("/"):
            next_node = node.GetNext(p)
            if next_node is None:
                new_node = Node()
                node.SetNext(p, new_node)
            node = node.GetNext(p)
        return node

    async def Set(self, path, data):
        await self.lock.acquire()
        node = self._GetNode(path)
        node.SetData(data)
        self.lock.release()

    async def Get(self, path: str):
        await self.lock.acquire()
        node = self._GetNode(path)
        data = node.GetData()
        self.lock.release()
        return data


keeper = Keeper()


def GetKeeper():
    return keeper
