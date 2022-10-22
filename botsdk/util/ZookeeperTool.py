from kazoo.client import KazooClient

from botsdk.util.Error import printTraceBack
from .GetModule import getBot
from json import dumps, loads

_zkClient = None


def GetBotByName(name: str):
    try:
        zk = KazooClient(hosts="127.0.0.1:2181")
        zk.start()
        if not zk.exists(f"/bot/{name}"):
            return None
        ret = getBot(loads(zk.get(f"/bot/{name}")[0].decode())["data"])
        zk.stop()
        return ret
    except Exception:
        pass
    return None


def GetZKClient():
    global _zkClient
    try:
        if _zkClient is None:
            _zkClient = KazooClient(hosts="127.0.0.1:2181")
        _zkClient.start()
    except Exception:
        printTraceBack()
        return None
    return _zkClient


def AddEphemeralNode(rootPath, name, data):
    zk = GetZKClient()
    if zk is None:
        return False
    try:
        try:
            if not zk.exists(rootPath):
                zk.create(rootPath)
        except Exception:
            printTraceBack()
            return False
        zk.create(
                f"{rootPath}/{name}",
                dumps(data).encode(),
                ephemeral=True
            )
    except Exception:
        printTraceBack()
        return False
    return True
