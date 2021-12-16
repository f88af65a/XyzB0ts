import base64
import json
import sqlite3
import sys

import redis
from botsdk.util.JsonConfig import getConfig


'''
id为0表示持久化的设置
'''


class Cookie:
    def getAllCookie(self):
        pass

    def getCookie(self, id: str, key: str = None):
        pass

    def setCookie(self, id: str, key: str, value):
        pass


class SqliteCookie(Cookie):
    def __init__(self):
        self.sqlPath = getConfig()["sqlPath"]
        self.conn = sqlite3.connect(self.sqlPath)
        self.cur = self.conn.cursor()
        self.cur.execute(
            ('''CREATE TABLE IF NOT EXISTS Cookie(id TEXT PRIMARYKEY '''
             '''UNIQUE NOT NULL, cookie TEXT NOT NULL)'''))
        self.conn.commit()
        self.cookieDict = dict()

    def getAllCookie(self):
        self.cur.execute('''SELECT * FROM Cookie''')
        sqlData = self.cur.fetchall()
        re = dict()
        for i in sqlData:
            re[i[0]] = json.loads(base64.b64decode(i[1]).decode("utf8"))
        return re

    def updateCookie(self, id: str, cookie: str = None):
        if cookie is None:
            if id in self.cookieDict:
                del self.cookieDict[id]
            return ""
        self.cookieDict[id] = cookie
        return cookie

    def getCookieByStr(self, id: str):
        if id in self.cookieDict:
            return self.cookieDict[id]
        self.cur.execute('''SELECT * FROM Cookie WHERE id="{0}"'''.format(id))
        re = self.cur.fetchall()
        if len(re) == 0:
            self.setCookieByStr(id, "{}")
            return self.updateCookie(id, "{}")
        return self.updateCookie(id, base64.b64decode(re[0][1]).decode("utf8"))

    def getCookieByDict(self, id: str):
        return json.loads(self, self.getCookieByStr(id))

    def setCookieByStr(self, id: str, cookie: str):
        self.cookieDict[id] = cookie
        self.cur.execute('''REPLACE INTO Cookie VALUES("{0}","{1}")'''.format(
            id, base64.b64encode(cookie.encode()).decode()))
        self.conn.commit()

    def setCookieByDict(self, id: str, cookie: dict):
        self.setCookieByStr(id, json.dumps(cookie))

    def getCookie(self, id: str, key: str = None):
        if key is None:
            return self.getCookieByDict(id)
        cookie = self.getCookieByDict(id)
        if key not in cookie:
            return None
        return cookie[key]

    def setCookie(self, id: str, key: str, value):
        if key == "":
            return None
        cookie = self.getCookieByDict(id)
        cookie[key] = value
        self.setCookieByDict(id, cookie)


class redisCookie(Cookie):
    def __init__(self):
        self.sql = redis.Redis(
            host="localhost", port=6379, decode_responses=True)

    def getAllCookie(self):
        re = dict()
        for i in self.sql.keys("*"):
            re[i] = json.loads(base64.decode(self.sql[i]).decode())
        return re

    def getCookieByDict(self, id):
        if id not in self.sql:
            self.sql[id] = base64.b64encode(b"{}").decode()
        return base64.b64decode(self.sql[id]).decode()

    def setCookieByDict(self, id, data):
        self.sql[id] = base64.b64encode(json.dumps(data).encode()).decode()

    def getCookie(self, id: str, key: str = None):
        if key is None:
            return self.getCookieByDict(id)
        cookie = self.sql.get(id)
        if key in cookie:
            return cookie[key]
        return None

    def setCookie(self, id: str, key: str, value):
        if key == "":
            return None
        cookie = self.getCookieByDict(id)
        cookie[key] = value
        self.setCookieByDict(id, cookie)


cookieDriver = None


def getCookieDriver():
    global cookieDriver
    if cookieDriver is None:
        cookieDriver = getattr(
            sys.modules[__name__],
            getConfig()["cookieDriver"])()
    return cookieDriver


def getCookie(id: str, key: str = None):
    getCookieDriver().getCookie(id, key)


def setCookie(id: str, key: str, value):
    getCookieDriver().setCookie(id, key, value)
