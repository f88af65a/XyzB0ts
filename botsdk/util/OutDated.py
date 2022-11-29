from .Error import debugPrint


def OutDated(func):
    debugPrint(f"使用以过时的函数{func.__name__}")
    return func
