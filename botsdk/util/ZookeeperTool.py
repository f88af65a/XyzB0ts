from kazoo.client import KazooClient
from .GetModule import getBot
from json import loads


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
