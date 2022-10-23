import os
import sys
from json import dumps, loads

from confluent_kafka import Producer

from botsdk.util.JsonConfig import getConfig
from botsdk.util.ZookeeperTool import GetZKClient


def deliveryReport(self, err, msg):
    if err is not None:
        print('Message delivery failed: {}'.format(err))
    else:
        print('Message delivered to {} [{}]'.format(
                msg.topic(), msg.partition()))


def BotControl(botData):
    inputData = input(
        f'''------{botData["botName"]}------\n'''
        '''0.添加一个BotService\n'''
        '''1.减少一个BotService\n'''
    )
    try:
        inputData = int(inputData)
    except Exception:
        print("请输入整数")
        return
    if inputData == 0:
        os.system(
                f'''{getConfig()["python"]} '''
                f'''service account="{dumps(botData)}"''')
    elif inputData == 1:
        p = Producer({'bootstrap.servers': 'localhost:9092'})
        p.poll(0)
        p.produce(
                "BotService",
                dumps(
                    {"code": 1, "data": botData["botName"]}
                    ).encode("utf8"),
                callback=deliveryReport)
        p.flush()


def RouterControl():
    inputData = input(
        '''------Router------\n'''
        '''0.添加一个Router\n'''
        '''1.减少一个Router\n'''
    )
    try:
        inputData = int(inputData)
    except Exception:
        print("请输入整数")
        return
    if inputData == 0:
        os.system(
                f'''{getConfig()["python"]} route''')
    elif inputData == 1:
        p = Producer({'bootstrap.servers': 'localhost:9092'})
        p.poll(0)
        p.produce(
                "routeList",
                dumps(
                    {"code": 1}
                    ).encode("utf8"),
                callback=deliveryReport)
        p.flush()
        p.stop()


def HandleControl():
    inputData = input(
        '''------Handle------\n'''
        '''0.添加一个Router\n'''
        '''1.减少一个Router\n'''
    )
    try:
        inputData = int(inputData)
    except Exception:
        print("请输入整数")
        return
    if inputData == 0:
        os.system(
                f'''{getConfig()["python"]} handle''')
    elif inputData == 1:
        p = Producer({'bootstrap.servers': 'localhost:9092'})
        p.poll(0)
        p.produce(
                "targetHandle",
                dumps(
                    {"code": 1}
                    ).encode("utf8"),
                callback=deliveryReport)
        p.flush()
        p.stop()


def start():
    os.chdir(sys.path[0])
    while True:
        os.system("clear")
        accounts = getConfig()["account"]
        accountProcess = {}
        for i in accounts:
            accountProcess[i["botName"]] = []
        zk = GetZKClient()
        processCount = {}
        if zk.exists("/BotProcess"):
            processList = zk.get_children("/BotProcess")
            for i in processList:
                processData = loads(zk.get(f"/BotProcess/{i}")[0].decode())
                if processData["type"] not in processCount:
                    processCount[processData["type"]] = 0
                processCount[processData["type"]] += 1
                if processData["type"] == "BotService":
                    accountProcess[processData["botName"]].append(processData)
        for i in accounts:
            print(f'''------{i["botName"]}------''')
            for j in i:
                print(f'''{j}: {i[j]}''')
            print(f'''BotService: {len(accountProcess[i["botName"]])}''')
        print("------各类型数量------")
        for i in processCount:
            print(f'''{i}: {processCount[i]}''')
        zk.stop()
        print("------Control------")
        for i in range(len(accounts)):
            print(f'''{i}.{accounts[i]["botName"]}''')
        print(f'''{len(accounts)}.router管理''')
        print(f'''{len(accounts) + 1}.handle管理''')
        print(f'''{len(accounts) + 2}.刷新''')
        print(f'''{len(accounts) + 3}.退出''')
        inputData = input("请输入操作\n")
        try:
            inputData = int(inputData)
        except Exception:
            continue
        if inputData < len(accounts):
            BotControl[accounts[inputData]]
        elif inputData == len(accounts):
            RouterControl()
        elif inputData == len(accounts) + 1:
            HandleControl()
        elif inputData == len(accounts) + 2:
            continue
        elif inputData == len(accounts) + 3:
            return


if __name__ == "__main__":
    start()
