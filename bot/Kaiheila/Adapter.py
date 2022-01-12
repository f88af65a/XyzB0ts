import json

import botsdk.util.HttpRequest
from botsdk.BotModule.Adapter import Adapter


class KaiheilaAdapter(Adapter):
    def init(self, data):
        self.url = data["path"]
        self.data["headers"] = {
            "Content-type": "application/json",
            "Authorization": (f"""{self.data["authorizationType"]}"""
                              f""" {self.data["token"]}""")
            }

    async def get(self, parameter, **kwargs):
        return json.loads(
            await botsdk.util.HttpRequest.get(
                (self.url + parameter["path"] + "?"
                 + "&".join(["=".join([i, kwargs[i]]) for i in kwargs])),
                headers=self.data["headers"]))

    async def post(self, parameter, **kwargs):
        return json.loads(
            await botsdk.util.HttpRequest.post(
                self.url + parameter["path"], kwargs,
                headers=self.data["headers"]))
