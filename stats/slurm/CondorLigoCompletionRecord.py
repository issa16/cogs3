# Represents a line of Condor LIGO log
# TSV file containing:
# JobID      Owner            LigoSearchTag                   Qdate           JobStartDate    CompletionDate MachineAttr RequestCpus CPUsUsage  RemoteUserCPU RemoteSysCPU RequestMemory MemoryUsage RemoteWallClockTime
# 1946186.1  geraint.pratten  aluk.dev.o3.cbc.pe.lalinference 1571652399      1571652400      0              85          1           undefined  0.0           0.0          150     u     undefined   0123546879


class CondorLigoCompletionRecord:

    def __init__(self, row=[]):
        if len(row) == 0:
            raise ValueError
        self.jobID = row['JobID']
        self.Owner = row['Owner']
        self.LigoSearchTag = row['LigoSearchTag']
        self.RequestCpus = row['RequestCpus']
        self.Qdate = row['Qdate']
        self.JobStartDate = row['JobStartDate']
        self.RemoteUserCPU = row['RemoteUserCPU']
        self.RemoteSysCPU = row['RemoteSysCPU']
        self.CompletionDate = row['CompletionDate']
        self.MachineAttr = row['MachineAttr']
        self.RemoteWallClockTime = row['RemoteWallClockTime']

    def __str__(self):
        retv = (
            'JobID={self.jobID} Owner={self.Owner} LigoSearchTag={self.LigoSearchTag} '
            'RequestCpus={self.RequestCpus} Qdate={self.Qdate} JobStartDate={self.JobStartDate} '
            'RemoteUserCPU={self.RemoteUserCPU} RemoteSysCPU={self.RemoteSysCPU} '
            'CompletionDate={self.CompletionDate} MachineAttr={self.MachineAttr} '
            'RemoteWallClockTime={self.RemoteWallClockTime}'
        )
        return retv
