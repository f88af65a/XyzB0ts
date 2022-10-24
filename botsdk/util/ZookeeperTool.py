from kazoo.client import KazooClient

from botsdk.util.Error import printTraceBack
from botsdk.util.JsonConfig import getConfig
from .GetModule import getBot
from json import dumps, loads

_zkClient = None


def GetBotByName(name: str):
    try:
        zk = GetZKClient()
        try:
            if not zk.exists(f"/Bot/{name}"):
                return None
        except Exception:
            zk.stop()
            printTraceBack()
            return None
        try:
            ret = getBot(loads(zk.get(f"/Bot/{name}")[0].decode())["data"])
        except Exception:
            zk.stop()
            printTraceBack()
        zk.stop()
        return ret
    except Exception:
        zk.stop()
    return None


def GetZKClient():
    global _zkClient
    try:
        if _zkClient is None:
            _zkClient = KazooClient(hosts=getConfig()["zookeeper"])
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
