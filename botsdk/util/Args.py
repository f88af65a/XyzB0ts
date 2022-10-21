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
