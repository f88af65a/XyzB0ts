import heapq
import time
import uuid
import asyncio


class Timer:
    def __init__(self):
        self.timerList = list()
        self.d = dict()

    # ratio:间隔,runSize:次数
    def addTimer(self, func, args: list, ratio=1, runSize=-1):
        if ratio == 0:
            raise
        while (uid := uuid.uuid4()) in self.d:
            pass
        thisTime = time.time()
        self.d[uid] = [thisTime + ratio, func, ratio, runSize, [uid] + args]
        heapq.heappush(self.timerList, self.d[uid])

    def delTimer(self, id):
        for i in range(0, len(self.timerList)):
            if self.timerList[i][4] == id:
                del self.timerList[i]
                del self.d[id]
                return True
        return False

    def getTimeOut(self):
        thisTime = time.time()
        re = []
        while len(self.timerList) > 0 and self.timerList[0][0] < thisTime:
            timer = heapq.heappop(self.timerList)
            re.append([timer[1], timer[4]])
            if timer[3] != -1:
                timer[3] -= 1
            if timer[3] != 0:
                timer[0] += timer[2]
                heapq.heappush(self.timerList, timer)
            else:
                del self.d[timer[4]]
        return re

    async def timerLoop(self):
        loop = asyncio.get_event_loop()
        while True:
            thisTime = time.time()
            wakeList = self.getTimeOut()
            for i in wakeList:
                asyncio.run_coroutine_threadsafe(i[0](*i[1]), loop)
            await asyncio.sleep(0.01 - (time.time() - thisTime))
