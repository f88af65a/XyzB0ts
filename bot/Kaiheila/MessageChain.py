from botsdk.BotModule.MessageChain import MessageChain


class KaiheilaMessageChain(MessageChain):
    def plain(self, data: str):
        self.data.append(
            {
                "type": "section",
                "text": {
                    "type": "plain-text",
                    "content": data
                }
            }
        )
        return self

    def image(self, url: str):
        self.data.append(
            {
                "type": "container",
                "elements": [
                    {
                        "type": "image",
                        "src": url
                    }
                ]
            }
        )
        return self
