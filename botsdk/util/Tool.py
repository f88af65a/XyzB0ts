from importlib import reload
from importlib import import_module


def getModuleByPath(path):
    return reload(import_module(path))


def getAttrFromModule(path, attr):
    return getattr(getModuleByPath(path), attr)
