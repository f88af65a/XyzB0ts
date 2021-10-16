import sqlite3
import base64
import json
from botsdk.tool.JsonConfig import getConfig

'''
-1表示config
0表示持久化的设置
'''
sqlPath = getConfig()["sqlPath"]
conn = sqlite3.connect(sqlPath)
cur = conn.cursor()
cur.execute('''CREATE TABLE IF NOT EXISTS GroupCookie(groupid TEXT PRIMARYKEY UNIQUE NOT NULL, cookie TEXT NOT NULL)''')
conn.commit()

cookieDict = dict()

def updateCookie(groupid : str, cookie : str = None):
    if cookie is None:
        if groupid in cookieDict:
            del cookieDict[groupid]
        return ""
    cookieDict[groupid] = cookie
    return cookie

def getCookieByStr(groupid : str):
    if groupid in cookieDict:
        return cookieDict[groupid]
    cur.execute('''SELECT * FROM GroupCookie WHERE groupid="{0}"'''.format(groupid))
    re = cur.fetchall()
    if len(re) == 0:
        changeCookieByStr(groupid, "{}")
        return updateCookie(groupid, "{}")
    return updateCookie(groupid, base64.b64decode(re[0][1]).decode("utf8"))

def getCookieByDict(groupid: str):
    if groupid == "-1":
        return getConfig()["systemCookie"]
    return json.loads(getCookieByStr(groupid))

def changeCookieByStr(groupid : str, cookie : str):
    cookieDict[groupid] = cookie
    cur.execute('''REPLACE INTO GroupCookie VALUES("{0}","{1}")'''.format(groupid, base64.b64encode(cookie.encode()).decode()))
    conn.commit()

def changeCookieByDict(groupid : str, cookie: dict):
    changeCookieByStr(groupid, json.dumps(cookie))

def getCookie(groupid : str, key : str):
    if key == "":
        return None
    cookie = getCookieByDict(groupid)
    if key not in cookie:
        return None
    return cookie[key]
    
def setCookie(groupid : str, key : str, value : str):
    if key == "":
        return None
    cookie = getCookieByDict(groupid)
    if value == "":
        if key in cookie:
            del cookie[key]
        else:
            return None
    else:
        cookie[key] = value
    changeCookieByDict(groupid, cookie)
