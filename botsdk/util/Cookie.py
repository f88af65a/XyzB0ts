import sqlite3
import base64
import json
from botsdk.util.JsonConfig import getConfig

'''
id为0表示持久化的设置
'''
sqlPath = getConfig()["sqlPath"]
conn = sqlite3.connect(sqlPath)
cur = conn.cursor()
cur.execute(('''CREATE TABLE IF NOT EXISTS Cookie(id TEXT PRIMARYKEY '''
             '''UNIQUE NOT NULL, cookie TEXT NOT NULL)'''))
conn.commit()
cookieDict = dict()


def getAllCookie():
    cur.execute('''SELECT * FROM Cookie''')
    sqlData = cur.fetchall()
    re = dict()
    for i in sqlData:
        re[i[0]] = json.loads(base64.b64decode(i[1]).decode("utf8"))
    return re


def updateCookie(id: str, cookie: str = None):
    if cookie is None:
        if id in cookieDict:
            del cookieDict[id]
        return ""
    cookieDict[id] = cookie
    return cookie


def getCookieByStr(id: str):
    if id in cookieDict:
        return cookieDict[id]
    cur.execute('''SELECT * FROM Cookie WHERE id="{0}"'''.format(id))
    re = cur.fetchall()
    if len(re) == 0:
        setCookieByStr(id, "{}")
        return updateCookie(id, "{}")
    return updateCookie(id, base64.b64decode(re[0][1]).decode("utf8"))


def getCookieByDict(id: str):
    return json.loads(getCookieByStr(id))


def setCookieByStr(id: str, cookie: str):
    cookieDict[id] = cookie
    cur.execute('''REPLACE INTO Cookie VALUES("{0}","{1}")'''.format(
        id, base64.b64encode(cookie.encode()).decode()))
    conn.commit()


def setCookieByDict(id: str, cookie: dict):
    setCookieByStr(id, json.dumps(cookie))


def getCookie(id: str, key: str = None):
    if key is None:
        return getCookieByDict(id)
    cookie = getCookieByDict(id)
    if key not in cookie:
        return None
    return cookie[key]


def setCookie(id: str, key: str, value):
    if key == "":
        return None
    cookie = getCookieByDict(id)
    cookie[key] = value
    setCookieByDict(id, cookie)
