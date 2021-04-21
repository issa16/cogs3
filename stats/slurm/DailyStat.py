import datetime


class DailyStat:

    # Zeroed default values
    def __init__(
        self,
        nj=0,
        twait=datetime.timedelta(0),
        tcpu=datetime.timedelta(0),
        twall=datetime.timedelta(0),
    ):
        # Create class variables needed here
        self.__numberJobs = nj
        self.__totalWaitTime = twait
        self.__totalCPUTime = tcpu
        self.__totalWallTime = twall

    def getNumberJobs(self):
        return self.__numberJobs

    def getTotalWaitTime(self):
        return self.__totalWaitTime

    def getTotalCPUTime(self):
        return self.__totalCPUTime

    def getTotalWallTime(self):
        return self.__totalWallTime

    def addValues(
        self,
        nj=0,
        twait=datetime.timedelta(0),
        tcpu=datetime.timedelta(0),
        twall=datetime.timedelta(0),
    ):
        self.__numberJobs += nj
        self.__totalWaitTime += twait
        self.__totalCPUTime += tcpu
        self.__totalWallTime += twall
