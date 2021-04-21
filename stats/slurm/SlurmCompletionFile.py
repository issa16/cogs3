import csv

from .SlurmCompletionRecord import SlurmCompletionRecord


class SlurmCompletionFile:
    # Initializer is called with an open file handle object opened to the
    #  Slurm completion log
    # \param fh An open file object to the accounting file.
    def __init__(self, fh):
        self.reader = csv.reader(fh, delimiter=' ', quotechar='"')

    def __iter__(self):
        return self

    # Iterator function is called each iteration and parses the next line of file for a completion record
    def __next__(self):
        try:
            j = SlurmCompletionRecord(self.reader.__next__())
        except ValueError:
            return 0
        return j
