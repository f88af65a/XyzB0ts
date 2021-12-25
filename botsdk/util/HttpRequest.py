import json

import aiohttp
from botsdk.util.Error import debugPrint, printTraceBack


async def get(url, proxy=None, headers=None, byte=None, timeout: int = 15):
    try:
        timeout = aiohttp.ClientTimeout(total=timeout)
        async with aiohttp.ClientSession(
                headers=(headers if headers is not None else None),
                timeout=timeout) as session:
            async with session.get(
                    url,
                    proxy=proxy if proxy is not None else None,
                    verify_ssl=False) as r:
                if byte is not None and byte:
                    return await r.read()
                return await r.text()
    except Exception:
        printTraceBack()
        debugPrint(f"请求{url}时发生异常")
        return None


async def post(url, data, byte=None, timeout: int = 15):
    try:
        timeout = aiohttp.ClientTimeout(total=timeout)
        async with aiohttp.ClientSession(
                timeout=timeout) as session:
            async with session.post(url, data=json.dumps(data).encode("utf8"),
                                    verify_ssl=False) as r:
                if byte is True:
                    return await r.read()
                return await r.text()
    except Exception:
        printTraceBack()
        debugPrint(f"请求{url}时发生异常")
        return None
