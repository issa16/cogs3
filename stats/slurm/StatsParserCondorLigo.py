#
# Stats parser for Condor log output from LIGO
#

from datetime import datetime, timedelta

from .CondorLigoCompletionFile import CondorLigoCompletionFile
from .CondorLigoCompletionRecord import CondorLigoCompletionRecord
from .DailyStatSparseArray import DailyStatSparseArray


class StatsParserCondorLigo:

    def __init__(self, condorlogfile, fordate):
        # TODO: check input file present & readable
        self.__logFile = condorlogfile
        self.__startDate = fordate
        self.__endDate = self.__startDate + timedelta(hours=23, minutes=59, seconds=59)
        self.__statsArray = DailyStatSparseArray()
        print("StatsParserCondorLigo: Created for ", self.__startDate, " to ", self.__endDate)

    def ParseNow(self):
        # Condor Ligo log field mapping:
        # owner -> user
        # ????    -> account
        # "condor" -> method (needs pre-pop)
        # "Default" -> application
        # RequestCPUs -> processorCount
        # ???? -> partition
        # 1 -> vNJobs
        # (JobStartDate - Qdate) -> waitTime
        # (RemoteUserCPU + RemoteSystemCPU) -> cpuTime
        # (CompletionDate - JobStartDate) -> wallTime

        # Example records:
        # JobID    Owner        LigoSearchTag                   Qdate      JobStartDate CompletionDate MachineAttr RequestCpus CPUsUsage          RemoteUserCPU RemoteSysCPU RequestMemory MemoryUsage RemoteWallClockTime
        # 670910.0 fergus.hayes aluk.sim.o3.cbc.pe.lalinference 1565821135 1565821142   0              85          1           0.9973175489878042 46567.0       24.0         1024          147
        # 670910.0 fergus.hayes aluk.sim.o3.cbc.pe.lalinference 1565821135 1565821142   0              85          1           0.9973175489878042 46567.0       24.0         1024          147         46605.0
        # 4111025.0 zu-cheng.chen ligo.dev.o3.cbc.explore.test  1575295887 1575295904   1575376312     85          2           0.9966176059934881 79704.0       573.0        4096          1221        80408.0

        print("ParseNowCondorLigo Starting")

        countLog = 0
        countLine = 0
        ignoredRecs = 0
        for i in CondorLigoCompletionFile(open(self.__logFile, 'r')):
            #
            #print(countLine,i)
            countLine = countLine + 1

            # Skip non valids
            if isinstance(i, CondorLigoCompletionRecord):
                #print(i)
                # if StartDate = undefined then it's a cancelled job before execution, so ignore
                #print(i.JobStartDate, type(i.JobStartDate))
                if i.JobStartDate == "undefined":
                    continue
                # if CompletionDate = 0 then it's a cancelled job during run so use JobStartDate+RemoteWallClockTime, otherwise stick with CompletionDate
                if int(i.CompletionDate) != 0:
                    recordDate = datetime.utcfromtimestamp((int(i.CompletionDate)))
                else:
                    # Occasionally a RemoteWallClockTime can be 'missing' so None :-(
                    if i.RemoteWallClockTime != None:
                        recordDate = datetime.utcfromtimestamp(
                            (int(i.JobStartDate) + int(float(i.RemoteWallClockTime)))
                        )
                    else:
                        recordDate = datetime.utcfromtimestamp((int(i.JobStartDate)))

                #print(recordDate,i.CompletionDate)
                # Check for right date and not completion date of zero (presumably still running)
                if recordDate >= self.__startDate and recordDate <= self.__endDate:
                    ## Debug
                    #print(countLog)
                    #print("ParseNow: ", countLog, i)
                    countLog = countLog + 1

                    #WaitTime
                    myWaitDuration = timedelta(seconds=(int(i.JobStartDate) - int(i.Qdate)))

                    #WallTime
                    # if CompetionDate = 0 then it's a cancelled job so use RemoteWallClockTime, otherwise stick with CompletionDate-JobStartDate
                    if int(i.CompletionDate) != 0:
                        myWallTime = int(i.CompletionDate) - int(i.JobStartDate)
                    else:
                        myWallTime = int(float(i.RemoteWallClockTime))
                    myComputeWallDuration = timedelta(seconds=(myWallTime * int(i.RequestCpus)))

                    # CPUusage and MemoryUsage in Condor log can be 'undefined' which means job was too short to be measured.
                    #   These will be converted as undefined=0 so can just be treated as normal
                    #cpuTime
                    mys = int(float(i.RemoteUserCPU)) + int(float(i.RemoteSysCPU))
                    #mys=int(float(i.RemoteUserCPU))
                    myCPUTime = timedelta(seconds=mys)

                    #Partition for Ligo is defined (from condor output) by MachineAttr value
                    if i.MachineAttr == "85":  #skylake
                        myQueue = "CF-c_compute_ligo1"
                    elif i.MachineAttr == "63":  #haswell
                        myQueue = "CF-c_compute_ligo2"
                    else:
                        myQueue = False

                    #Examine the LigoSearchTag and set the application profile, including creating a new one if necessary
                    # format:   i.LigoSearchTag="ligo.prod.o3.cbc.grb.cohptfoffline"
                    lst_bits = i.LigoSearchTag.split(".")
                    if len(lst_bits) == 6:
                        myApp = lst_bits[3] + "." + lst_bits[4] + "." + lst_bits[5]
                    else:
                        myApp = False

                    #print(i.Owner,"scw1158","CONDOR",myApp,i.RequestCpus,myQueue,1,myWaitDuration,myCPUTime,myComputeWallDuration)

                    self.__statsArray.Add(
                        userName=i.Owner,
                        projectCode="scw1158",
                        subMethod="CONDOR",
                        execApp=myApp,
                        execNCPU=i.RequestCpus,
                        execQueue=myQueue,
                        vNJobs=1,
                        vWaitTime=myWaitDuration,
                        vCPUTime=myCPUTime,
                        vWallTime=myComputeWallDuration
                    )
            else:
                ignoredRecs += 1
                print(i)
        print("Found " + str(ignoredRecs) + " ignored records")

    def PrintResultsArray(self):
        self.__statsArray.PrintByUser()

    def PrintResultsArrayTree(self):
        self.__statsArray.PrintAsTree()

    def getResultsArray(self):
        return self.__statsArray

    def getArraySize(self):
        return (self.__statsArray.getSize())
