import aiohttp
import json
from botsdk.tool.Error import printTraceBack

async def get(url, proxy = None, headers = None, byte = None):
    try:
        async with aiohttp.ClientSession(headers = headers if headers is not None else None) as session:
            async with session.get(url, proxy = proxy if proxy is not None else None, verify_ssl=False) as r:
                if byte is not None and byte:
                    return await r.read()
                return await r.text()
    except Exception as e:
        printTraceBack()
        return None

async def post(url, data, byte = None):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=json.dumps(data).encode("utf8"),verify_ssl=False) as r:
                if byte is True:
                    return await r.read()
                return await r.text()
    except Exception as e:
        printTraceBack()
        return None
