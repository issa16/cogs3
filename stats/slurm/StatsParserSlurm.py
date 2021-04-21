from datetime import datetime, timedelta

from .DailyStatSparseArray import DailyStatSparseArray
from .SlurmCompletionFile import SlurmCompletionFile
from .SlurmCompletionRecord import SlurmCompletionRecord


class StatsParserSlurm:

    def __init__(self, slurmfile, fordate):
        print(slurmfile, fordate)
        # TODO: check input file present & readable
        self.__logFile = slurmfile
        self.__startDate = fordate
        self.__endDate = self.__startDate + timedelta(hours=23, minutes=59, seconds=59)
        self.__statsArray = DailyStatSparseArray()
        print("StatsParser: Created for ", self.__startDate, " to ", self.__endDate)

    def ParseNow(self):
        # A line of SLurm completion log:
        # JobId=64652 UserId=ivan.scivetti(16780386) GroupId=ivan.scivetti(16780386) Name=vasp_test JobState=CANCELLED Partition=cpc TimeLimit=600 StartTime=2015-09-21T22:24:46 EndTime=2015-09-21T23:27:13 NodeList=ssc[029-032] NodeCnt=4 ProcCnt=64 WorkDir=/scratch/ivan.scivetti/LiMn2O4/Ni_BATTERY/PW91/K/conf1/no-U/ox_Ni_fixed/2-NiO2/K/3.66Ni_new/6K/18_h2o
        # jobid | userid | groupid | name | state | partition | timelimit | starttime | endtime | nodelist | nodecount | processor count | workdir
        print("ParseNowSlurm Starting")

        countLog = 0
        countLine = 0
        for i in SlurmCompletionFile(open(self.__logFile, 'r')):
            countLine = countLine + 1

            # Skip non valids
            if isinstance(i, SlurmCompletionRecord):
                recordDate = datetime.strptime(i.endTime, "%Y-%m-%dT%H:%M:%S")
                if isinstance(
                    i, SlurmCompletionRecord
                ) and recordDate >= self.__startDate and recordDate <= self.__endDate:
                    countLog = countLog + 1

                    # Use allocCPU from Slurm where possible as this reflects the exclusive use of
                    # nodes (i.e. is 16 for an n=1, exclusive job and 1 for n=1,non-exclusive job)
                    # But CANCELLED jobs do not necesarilly have an allocation value
                    if (i.jobState == "CANCELLED" or i.jobState == "FAILED"):
                        myProcessorCount = i.processorCount
                    else:
                        myProcessorCount = i.allocCPU
                    # Sigh, can be zero when cancelled, zero-time job, bodge....
                    #print(myProcessorCount)
                    if (myProcessorCount == "0" or myProcessorCount == ""):
                        myProcessorCount = "1"
                    #print(myProcessorCount)

                    # durations
                    myStart = datetime.strptime(i.startTime, "%Y-%m-%dT%H:%M:%S")
                    myEnd = datetime.strptime(i.endTime, "%Y-%m-%dT%H:%M:%S")
                    mySubmit = datetime.strptime(i.submitTime, "%Y-%m-%dT%H:%M:%S")
                    myWallDuration = myEnd - myStart
                    myWaitDuration = myStart - mySubmit
                    myComputeWallDuration = myWallDuration * int(myProcessorCount)
                    # possible cputime format:  1-04:42:40    or  04:42:40    or   04:43.333
                    if '.' in i.cpuTime:  # minutes:seconds.decimal
                        fullminutes = i.cpuTime.split(':')
                        fullseconds = i.cpuTime.split(':')
                        miniseconds = fullseconds[1].split('.')
                        days = 0
                        hours = 0
                        minutes = fullminutes[0]
                        seconds = miniseconds[0]
                    elif '-' in i.cpuTime:  # days-hours:minutes:seconds
                        fulltime = i.cpuTime.split('-')
                        fullhours = fulltime[1].split(':')
                        days = fulltime[0]
                        hours = fullhours[0]
                        minutes = fullhours[1]
                        seconds = fullhours[2]
                    else:  #hours:minutes:seconds
                        fullhours = i.cpuTime.split(':')
                        days = 0
                        hours = fullhours[0]
                        minutes = fullhours[1]
                        seconds = fullhours[2]
                    myCPUTimeS = ((int(days) * 60 * 60 * 24) + (int(hours) * 60 * 60) + (int(minutes) * 60) +
                                  (int(seconds)))
                    myCPUTime = timedelta(seconds=myCPUTimeS)

                    jobYear = myEnd.year
                    jobMonth = myEnd.month

                    userfields = i.userID.split('(')
                    myUser = userfields[0]

                    if (myUser == "root"):
                        myUser = "software.builder"
                        myAccount = "scw1001"
                    else:
                        myAccount = i.account

                    self.__statsArray.Add(
                        myUser,
                        myAccount,
                        "SSH",
                        "Default",
                        myProcessorCount,
                        i.partition,
                        vNJobs=1,
                        vWaitTime=myWaitDuration,
                        vCPUTime=myCPUTime,
                        vWallTime=myComputeWallDuration
                    )

    def PrintResultsArray(self):
        self.__statsArray.PrintByUser()

    def PrintResultsArrayTree(self):
        self.__statsArray.PrintAsTree()

    def getResultsArray(self):
        return self.__statsArray

    def getArraySize(self):
        return (self.__statsArray.getSize())
