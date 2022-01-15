import json

import aiohttp
from botsdk.util.Error import debugPrint, printTraceBack


conn = None


async def get(url, proxy=None, headers=None, byte=None, timeout: int = 15):
    global conn
    if conn is None:
        conn = aiohttp.TCPConnector()
    try:
        timeout = aiohttp.ClientTimeout(total=timeout)
        async with aiohttp.ClientSession(
                headers=headers,
                connector=conn,
                connector_owner=False,
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


async def post(url, data, headers=None, byte=None, timeout: int = 15):
    global conn
    if conn is None:
        conn = aiohttp.TCPConnector()
    try:
        timeout = aiohttp.ClientTimeout(total=timeout)
        async with aiohttp.ClientSession(
                connector=conn,
                connector_owner=False,
                timeout=timeout) as session:
            async with session.post(url, data=json.dumps(data).encode("utf8"),
                                    headers=headers,
                                    verify_ssl=False) as r:
                if byte is True:
                    return await r.read()
                return await r.text()
    except Exception:
        printTraceBack()
        debugPrint(f"请求{url}时发生异常")
        return None
