from botsdk.tool.Error import debugPrint

def OutDated(func):
    def warp(*args, **kwargs):
        debugPrint(f"使用以过时的函数{func.__name__}")
        return func(*args, **kwargs)
    return warp