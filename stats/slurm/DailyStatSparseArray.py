import datetime

from .DailyStat import DailyStat


class DailyStatSparseArray:

    def __init__(self):
        self.__statsArray = {}  # Top-level empty dictionary

    # Create a new entry in the multi-dimenional dict
    #  -parameters starting with a 'v' are values for the created object
    def __Create(self, userName, projectCode, subMethod, execApp, execNCPU, execQueue):
        # -dictionary creation
        if not userName in self.__statsArray:
            self.__statsArray[userName] = {}
        if not projectCode in self.__statsArray[userName]:
            self.__statsArray[userName][projectCode] = {}
        if not subMethod in self.__statsArray[userName][projectCode]:
            self.__statsArray[userName][projectCode][subMethod] = {}
        if not execApp in self.__statsArray[userName][projectCode][subMethod]:
            self.__statsArray[userName][projectCode][subMethod][execApp] = {}
        if not execNCPU in self.__statsArray[userName][projectCode][subMethod][execApp]:
            self.__statsArray[userName][projectCode][subMethod][execApp][execNCPU] = {}
        if not execQueue in self.__statsArray[userName][projectCode][subMethod][execApp][execNCPU]:
            self.__statsArray[userName][projectCode][subMethod][execApp][execNCPU][execQueue] = DailyStat()

    def __Exists(self, userName, projectCode, subMethod, execApp, execNCPU, execQueue):
        if userName in self.__statsArray:
            if projectCode in self.__statsArray[userName]:
                if subMethod in self.__statsArray[userName][projectCode]:
                    if execApp in self.__statsArray[userName][projectCode][subMethod]:
                        if execNCPU in self.__statsArray[userName][projectCode][subMethod][execApp]:
                            if execQueue in self.__statsArray[userName][projectCode][subMethod][execApp][execNCPU]:
                                return True
                            else:
                                return False
                        else:
                            return False
                    else:
                        return False
                else:
                    return False
            else:
                return False
        else:
            return False

    # Add actual values, assume it exists
    def __AddValues(
        self, userName, projectCode, subMethod, execApp, execNCPU, execQueue, vNJobs, vWaitTime, vCPUTime, vWallTime
    ):
        self.__statsArray[userName][projectCode][subMethod][execApp][execNCPU][execQueue].addValues(
            nj=vNJobs, twait=vWaitTime, tcpu=vCPUTime, twall=vWallTime
        )

    # Trick function to handle addition/creation as necessary
    def Add(
        self,
        userName,
        projectCode,
        subMethod,
        execApp,
        execNCPU,
        execQueue,
        vNJobs=0,
        vWaitTime=datetime.timedelta(0),
        vCPUTime=datetime.timedelta(0),
        vWallTime=datetime.timedelta(0)
    ):
        if not self.__Exists(userName, projectCode, subMethod, execApp, execNCPU, execQueue):
            self.__Create(userName, projectCode, subMethod, execApp, execNCPU, execQueue)
        self.__AddValues(
            userName, projectCode, subMethod, execApp, execNCPU, execQueue, vNJobs, vWaitTime, vCPUTime, vWallTime
        )

    def Print(self):
        print(self.__statsArray)

    def PrintByUser(self):
        for key in self.__statsArray.keys():
            print(key, ":", self.__statsArray[key])

    def PrintAsTree(self):
        for myUserName in self.__statsArray.keys():
            for myProjectCode in self.__statsArray[myUserName].keys():
                for mySubMethod in self.__statsArray[myUserName][myProjectCode].keys():
                    for myExecApp in self.__statsArray[myUserName][myProjectCode][mySubMethod].keys():
                        for myExecNCPU in self.__statsArray[myUserName][myProjectCode][mySubMethod][myExecApp].keys():
                            for myExecQueue in self.__statsArray[myUserName][myProjectCode][mySubMethod][myExecApp][
                                myExecNCPU].keys():
                                print(
                                    "DS:", myUserName, myProjectCode, mySubMethod, myExecApp, myExecNCPU, myExecQueue,
                                    self.__statsArray[myUserName][myProjectCode][mySubMethod][myExecApp][myExecNCPU]
                                    [myExecQueue].getNumberJobs(), self.__statsArray[myUserName][myProjectCode]
                                    [mySubMethod][myExecApp][myExecNCPU][myExecQueue].getTotalWallTime(),
                                    self.__statsArray[myUserName][myProjectCode][mySubMethod][myExecApp][myExecNCPU]
                                    [myExecQueue].getTotalCPUTime()
                                )

    def __iter__(self):
        # iterator startup, first, 'multiply out' the dicts of dicts into a list
        self.iterlist = list()
        count = 0
        for myUserName in self.__statsArray.keys():
            for myProjectCode in self.__statsArray[myUserName].keys():
                for mySubMethod in self.__statsArray[myUserName][myProjectCode].keys():
                    for myExecApp in self.__statsArray[myUserName][myProjectCode][mySubMethod].keys():
                        for myExecNCPU in self.__statsArray[myUserName][myProjectCode][mySubMethod][myExecApp].keys():
                            for myExecQueue in self.__statsArray[myUserName][myProjectCode][mySubMethod][myExecApp][
                                myExecNCPU].keys():
                                myItem = {
                                    'userName': myUserName,
                                    'projectCode': myProjectCode,
                                    'subMethod': mySubMethod,
                                    'execApp': myExecApp,
                                    'execNCPU': myExecNCPU,
                                    'execQueue': myExecQueue,
                                    'nJobs':
                                        self.__statsArray[myUserName][myProjectCode][mySubMethod][myExecApp][myExecNCPU]
                                        [myExecQueue].getNumberJobs(),
                                    'waitTime':
                                        self.__statsArray[myUserName][myProjectCode][mySubMethod][myExecApp][myExecNCPU]
                                        [myExecQueue].getTotalWaitTime(),
                                    'cpuTime':
                                        self.__statsArray[myUserName][myProjectCode][mySubMethod][myExecApp][myExecNCPU]
                                        [myExecQueue].getTotalCPUTime(),
                                    'wallTime':
                                        self.__statsArray[myUserName][myProjectCode][mySubMethod][myExecApp][myExecNCPU]
                                        [myExecQueue].getTotalWallTime()
                                }
                                self.iterlist.append(myItem)
                                count += 1
        self.itercount = 0
        return self

    def getSize(self):
        sum = 0
        for myUserName in self.__statsArray.keys():
            for myProjectCode in self.__statsArray[myUserName].keys():
                for mySubMethod in self.__statsArray[myUserName][myProjectCode].keys():
                    for myExecApp in self.__statsArray[myUserName][myProjectCode][mySubMethod].keys():
                        for myExecNCPU in self.__statsArray[myUserName][myProjectCode][mySubMethod][myExecApp].keys():
                            for myExecQueue in self.__statsArray[myUserName][myProjectCode][mySubMethod][myExecApp][
                                myExecNCPU].keys():
                                sum += (
                                    self.__statsArray[myUserName][myProjectCode][mySubMethod][myExecApp][myExecNCPU]
                                    [myExecQueue].getNumberJobs()
                                )
        return sum

    def __next__(self):
        # return the next member of the list until all done
        if self.itercount < len(self.iterlist):
            self.itercount += 1
            return self.iterlist[(self.itercount - 1)]
        else:
            raise StopIteration
