import heapq
import time
import uuid
import asyncio


class Timer:
    def __init__(self):
        self.timerList = list()
        self.d = dict()

    # ratio:间隔,runSize:次数
    def addTimer(self, func, ratio=1, runSize=-1):
        if ratio == 0:
            raise
        while (id := uuid.uuid4()) not in self.d:
            pass
        thisTime = time.time()
        self.d[id] = (thisTime + ratio, func, ratio, runSize, id)
        heapq.heappush(self.timerList, self.d[id])

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
        while len(self.timerList) > 0 and self.timerList[0][0] > thisTime:
            timer = heapq.heappop(self.timerList)
            re.append([timer[1], timer[4]])
            if timer[3] != -1:
                timer[3] -= 1
            if timer[3] != 0:
                timer[0] += timer[2]
            else:
                del self.d[timer[4]]
        return re

    async def timerLoop(self):
        loop = asyncio.get_event_loop()
        while True:
            thisTime = time.time()
            wakeList = self.getTimeOut()
            for i in wakeList:
                asyncio.run_coroutine_threadsafe(loop, i[0](i[1]))
            await asyncio.sleep(thisTime + 0.01)
