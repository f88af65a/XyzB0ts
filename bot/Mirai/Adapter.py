import botsdk.util.HttpRequest
import json
from botsdk.BotModule.Adapter import Adapter


class MiraiAdapter(Adapter):
    def init(self, data):
        self.url = data["path"]

    async def get(self, parameter, **kwargs):
        return json.loads(
            await botsdk.util.HttpRequest.get(
                (self.url + parameter["path"] + "?"
                 + "&".join(["=".join([i, kwargs[i]]) for i in kwargs]))))

    async def post(self, parameter, **kwargs):
        return json.loads(
            await botsdk.util.HttpRequest.post(
                self.url + parameter["path"], kwargs))
