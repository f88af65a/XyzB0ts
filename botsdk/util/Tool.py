from importlib import reload
from importlib import import_module
from kazoo.client import KazooClient
from ..util.GetModule import getBot
from json import loads


def getModuleByPath(path):
    return reload(import_module(path))


def getAttrFromModule(path, attr):
    return getattr(getModuleByPath(path), attr)


def getBotByName(name: str):
    try:
        zk = KazooClient(hosts="127.0.0.1:2181")
        zk.start()
        if not zk.exists(f"/bot/{name}"):
            return None
        return getBot(loads(zk.get(f"/bot/{name}").decode()))
    except Exception:
        pass
    return None
