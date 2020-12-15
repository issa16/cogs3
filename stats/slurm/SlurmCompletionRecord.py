#  Represents a Slurm job completion record
# A line of SLurm completion log:
# JobId=64652 UserId=ivan.scivetti(16780386) GroupId=ivan.scivetti(16780386) Name=vasp_test JobState=CANCELLED Partition=cpc TimeLimit=600 StartTime=2015-09-21T22:24:46 EndTime=2015-09-21T23:27:13 NodeList=ssc[029-032] NodeCnt=4 ProcCnt=64 WorkDir=/scratch/ivan.scivetti/LiMn2O4/Ni_BATTERY/PW91/K/conf1/no-U/ox_Ni_fixed/2-NiO2/K/3.66Ni_new/6K/18_h2o cpuTime=xyz account=hpcwx01 alloccpu=16
# jobid | userid | groupid | name | state | partition | timelimit | starttime | endtime | nodelist | nodecount | processor count | workdir | cputime


class SlurmCompletionRecord:

    def __init__(self, row=[]):
        if len(row) == 0:
            raise ValueError
        self.jobID = row.pop(0).split("=")[1].rstrip()
        self.userID = row.pop(0).split("=")[1].rstrip()
        if self.userID.startswith('('):
            self.userID = "software.builder"  # system default, must have been during the pre-production with non-final name service content, so let's allocate by default to dear old s.b
        self.groupID = row.pop(0).split("=")[1].rstrip()
        self.jobName = row.pop(0).split("=")[1].rstrip()
        while not row[0].startswith("JobState"):
            row.pop(0)
        self.jobState = row.pop(0).split("=")[1].rstrip()
        while not row[0].startswith("Partition"):
            row.pop(0)
        if "," in row[0]:
            self.partition = row.pop(0).split("=")[1].split(",")[0].rstrip()
        else:
            self.partition = row.pop(0).split("=")[1].rstrip()
        self.timeLimit = row.pop(0).split("=")[1].rstrip()
        self.startTime = row.pop(0).split("=")[1].rstrip()
        self.endTime = row.pop(0).split("=")[1].rstrip()
        self.nodeList = row.pop(0).split("=")[1].rstrip()
        while not row[0].startswith("NodeCnt"):
            row.pop(0)
        self.nodeCount = row.pop(0).split("=")[1].rstrip()
        self.processorCount = row.pop(0).split("=")[1].rstrip()
        self.workDir = row.pop(0).split("=")[1].rstrip()
        while row[0].split("=")[
            0
        ] != "cpuTime":  # A rare (once?) occurrence of an extra, (space seperated) output between jobName and jobState
            row.pop(0)
        self.cpuTime = row.pop(0).split("=")[1].rstrip()
        self.account = row.pop(0).split("=")[1].rstrip()
        if self.account == '':
            self.account = "scw1001"  # system default, must have been during pre-production
        self.allocCPU = row.pop(0).split("=")[1].rstrip()
        self.submitTime = row.pop(0).split("=")[1].rstrip()

    def __str__(self):
        retv = "JobID=" + self.jobID + " userID=" + self.userID + " groupID=" + self.groupID + " jobName=" + self.jobName + " jobState=" + self.jobState + " partition=" + self.partition + " timeLimit=" + self.timeLimit + " startTime=" + self.startTime + " endTime=" + self.endTime + " nodeList=" + self.nodeList + " nodeCount=" + self.nodeCount + " processorCount=" + self.processorCount + " workDir=" + self.workDir + " cpuTime=" + self.cpuTime + " account=" + self.account + " allocCPU=" + self.allocCPU + " submitTime=" + self.submitTime
        return retv
