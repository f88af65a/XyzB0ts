from sys import argv

_args = None


def GetArgs():
    global _args
    if _args is None:
        _args = {}
        for i in argv:
            for j in range(len(i)):
                if i[j] == '=':
                    _args[i[:j]] = i[j + 1:]
                    break
                if j == len(i) - 1:
                    _args[i] = ""
    return _args


class ArgParser:
    def __init__(self, help=None):
        self.prev = "-"
        self.actionList = list()
        self.positionalList = list()
        self.optionalMap = dict()
        self.help = help
        self.Add(
            "-h", "--help",
            NoneOpt=True,
            required=False,
            meta="参数",
            help="查看帮助"
        )

    def Add(self, *args, **kwargs):
        if not len(args):
            raise Exception("缺少参数")
        action = Action(*args, **kwargs)
        if not args[0].startswith(self.prev):
            action.SetDest(args[0])
            self.positionalList.append(len(self.actionList))
        else:
            for i in action.GetOptionals():
                if not i.startswith(self.prev):
                    raise Exception("Optionals参数缺少-")
                if i.startswith(self.prev * 2):
                    action.SetDest(i[2:])
                self.optionalMap[i] = len(self.actionList)
            if not action.GetDest():
                action.SetDest(args[0])
        self.actionList.append(action)

    def Parse(self, args: list):
        # positional位置
        positionalMark = 0
        # consume消耗到的位置
        consumeMark = 0
        # 当前解析到的arg位置
        argMark = 0
        usedAction = set()
        space = Space()
        action = None
        while consumeMark < len(args):

            if consumeMark == argMark:
                arg = args[argMark]
                if arg.startswith(self.prev):
                    if arg not in self.optionalMap:
                        raise Exception(f"{arg}不存在")
                    action = self.actionList[self.optionalMap[arg]]
                    argMark += 1
                    continue
                else:
                    if positionalMark >= len(self.positionalList):
                        raise Exception(f"{arg}位置参数过多")
                    action = self.actionList[
                            self.positionalList[positionalMark]]
                    positionalMark += 1
            if argMark >= len(args):
                arg = None
            else:
                arg = args[argMark]
            if arg is None and not action.IsNoneOpt():
                raise Exception(f"{action.GetDest()}参数不能为空")
            action(space, arg)
            argMark += 1
            consumeMark = argMark
            usedAction.add(action)
        if "help" not in space:
            for i in self.actionList:
                if i.GetRequired() and i not in usedAction:
                    raise Exception(f"缺少参数{i.GetDest()}")
        return space

    def GetAllHelp(self):
        if self.help:
            ret = f"{self.help}\n"
        else:
            ret = ""
        for i in range(len(self.actionList)):
            action = self.actionList[i]
            isOptional = False
            if action.GetOptionals()[0].startswith("-"):
                isOptional = True
            if action.GetRequired():
                ret += "["
            ret += f'''{"/".join(action.GetOptionals())}'''
            if isOptional:
                ret += f''' {action.GetMeta()}'''
            if action.GetRequired():
                ret += "]"
            if i != len(self.actionList):
                ret += " "
        ret += "\n"
        for i in range(len(self.actionList)):
            action = self.actionList[i]
            isOptional = False
            if action.GetOptionals()[0].startswith("-"):
                isOptional = True
            if isOptional:
                ret += (
                        f'''{"/".join(action.GetOptionals())} '''
                        f'''{action.GetHelp()}'''
                )
            else:
                ret += f'''{action.GetDest()} {action.GetHelp()}'''
            if i != len(self.actionList):
                ret += "\n"
        return ret

    def GetHelp(self, destOrOpt):
        for i in self.actionList:
            isOptional = False
            if i.GetOptionals()[0].startswith("-"):
                isOptional = True
            if (i.GetDest() == destOrOpt or destOrOpt in i.GetOptionals):
                if isOptional:
                    return (
                            f'''{"/".join(i.GetOptionals())} '''
                            f'''{i.GetHelp()}'''
                    )
                return f'''{i.GetDest()} {i.GetHelp()}'''
        raise BaseException(f"{destOrOpt} 不存在")


class Action:
    def __init__(self, *args, **kwargs):
        self.opt = kwargs
        self.dest = None
        self.optionals = args
        if "type" not in kwargs:
            self.opt["type"] = str
        if "required" not in kwargs:
            self.opt["required"] = True
        if "help" not in kwargs:
            self.opt["help"] = ""
        if "meta" not in kwargs:
            self.opt["meta"] = "N"
        if "NoneOpt" not in kwargs:
            self.opt["NoneOpt"] = False

    def __call__(self, space, value):
        space[self.GetDest()] = value

    def SetDest(self, dest):
        self.dest = dest

    def GetDest(self):
        return self.dest

    def AddOptionals(self, value):
        self.optionals.append(value)

    def GetOptionals(self):
        return self.optionals

    def GetType(self):
        return self.opt["type"]

    def GetRequired(self):
        return self.opt["required"]

    def GetHelp(self):
        return self.opt["help"]

    def GetMeta(self):
        return self.opt["meta"]

    def IsNoneOpt(self):
        return self.opt["NoneOpt"]


class Space(dict):
    def __missing__(self, key):
        return None
