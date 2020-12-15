#14/11/13 - Updated for Python 3, AF.
#22/09/15 - New for Slurm, AF.
#23/10/19 - New for Condor Ligo, AF.

import csv

from . import CondorLigoCompletionRecord


class CondorLigoCompletionFile:
    # Initializer is called with an open file handle object opened to the
    # Condor Ligo completion log
    # TSV file containing:
    # JobID,Owner,LigoSearchTag,Qdate,JobStartDate,CompletionDate,MachineAttr,RequestCpus,CPUsUsage,RemoteUserCPU,RemoteSysCPU,RequestMemory,MemoryUsage,RemoteWallClockTime
    # \param fh An open file object to the accounting file.
    def __init__(self, fh):
        fields = [
            'JobID',
            'Owner',
            'LigoSearchTag',
            'Qdate',
            'JobStartDate',
            'CompletionDate',
            'MachineAttr',
            'RequestCpus',
            'CPUsUsage',
            'RemoteUserCPU',
            'RemoteSysCPU',
            'RequestMemory',
            'MemoryUsage',
            'RemoteWallClockTime',
        ]
        self.reader = csv.DictReader(
            fh,
            dialect='excel-tab',
            fieldnames=fields,
        )

    def __iter__(self):
        return self

    # Iterator function is called each iteration and parses the next line of file for a completion record
    def __next__(self):
        try:
            j = CondorLigoCompletionRecord.CondorLigoCompletionRecord(self.reader.__next__())
        except ValueError:
            return 0
        return j
