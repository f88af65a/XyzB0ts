from .JsonConfig import getConfig
from .Tool import getAttrFromModule


def getRequest(data):
    return getAttrFromModule(
        ((getConfig()["botPath"]
         + data[0]["bot"][0]["botType"]).replace("/", ".")
         + ".Request"),
        data[0]["bot"][0]["botType"] + "Request")(*data)


def getBot(data):
    return getAttrFromModule(
                (getConfig()["botPath"]
                 + data[0]["botType"]).replace("/", ".") + ".Bot",
                data[0]["botType"] + "Bot")(*data)


def getAdapter(data):
    return getAttrFromModule(
        getConfig()["botPath"].replace("/", ".")
        + data["botType"] + ".Adapter", f"""{data["botType"]}Adapter""")(data)
