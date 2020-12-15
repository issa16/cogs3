TERMINFO = {
    "-1": {
        "name": "TERM_UNTERMINATED",
        "desc": "Job was not terminaed",
        "number": -1,
    },
    "0": {
        "name": "TERM_UNKNOWN",
        "desc": "LSF cannot determine a termination reason.0 is logged but TERM_UNKNOWN is not displayed (0)",
        "number": 0,
    },
    "1": {
        "name": "TERM_PREEMPT",
        "desc": "Job killed after preemption (1)",
        "number": 1,
    },
    "2": {
        "name": "TERM_WINDOW",
        "desc": "Job killed after queue run window closed (2)",
        "number": 2,
    },
    "3": {
        "name": "TERM_LOAD",
        "desc": "Job killed after load exceeds threshold (3)",
        "number": 3,
    },
    "4": {
        "name": "TERM_OTHER",
        "desc": "NOT SPECIFIED",
        "number": 4,
    },
    "5": {
        "name": "TERM_RUNLIMIT",
        "desc": "Job killed after reaching LSF run time limit (5)",
        "number": 5,
    },
    "6": {
        "name": "TERM_DEADLINE",
        "desc": "Job killed after deadline expires (6)",
        "number": 6,
    },
    "7": {
        "name": "TERM_PROCESSLIMIT",
        "desc": "Job killed after reaching LSF process limit (7)",
        "number": 7,
    },
    "8": {
        "name": "TERM_FORCE_OWNER",
        "desc": "Job killed by owner without time for cleanup (8)",
        "number": 8,
    },
    "9": {
        "name": "TERM_FORCE_ADMIN",
        "desc": "Job killed by root or LSF administrator without time for cleanup (9)",
        "number": 9,
    },
    "10": {
        "name": "TERM_REQUEUE_OWNER",
        "desc": "Job killed and requeued by owner (10)",
        "number": 10,
    },
    "11": {
        "name": "TERM_REQUEUE_ADMIN",
        "desc": "Job killed and requeued by root or LSF administrator (11)",
        "number": 11,
    },
    "12": {
        "name": "TERM_CPULIMIT",
        "desc": "Job killed after reaching LSF CPU usage limit (12)",
        "number": 12,
    },
    "13": {
        "name": "TERM_CHKPNT",
        "desc": "Job killed after checkpointing (13)",
        "number": 13,
    },
    "14": {
        "name": "TERM_OWNER",
        "desc": "Job killed by owner (14)",
        "number": 14,
    },
    "15": {
        "name": "TERM_ADMIN",
        "desc": "Job killed by root or LSF administrator (15)",
        "number": 15,
    },
    "16": {
        "name": "TERM_MEMLIMIT",
        "desc": "Job killed after reaching LSF memory usage limit (16)",
        "number": 16,
    },
    "17": {
        "name": "TERM_EXTERNAL_SIGNAL",
        "desc": "Job killed by a signal external to LSF (17)",
        "number": 16,
    },
    "18": {
        "name": "TERM_RMS",
        "desc": "NOT SPECIFIED",
        "number": 18,
    },
    "19": {
        "name": "TERM_ZOMBIE",
        "desc": "Job exited while LSF is not available (19)",
        "number": 19,
    },
    "20": {
        "name": "TERM_SWAP",
        "desc": "Job killed after reaching LSF swap usage limit (20)",
        "number": 20,
    },
    "21": {
        "name": "TERM_THREADLIMIT",
        "desc": "Job killed after reaching LSF thread limit (21)",
        "number": 21,
    },
    "22": {
        "name": "TERM_SLURM",
        "desc": "Job terminated abnormally in SLURM (node failure) (22)",
        "number": 22,
    },
    "23": {
        "name": "TERM_BUCKET_KILL",
        "desc": "Job killed with bkill -b (23)",
        "number": 23,
    },
}


class TermInfo:
    '''
    When a job is terminated, LSF stores details on the reason why the job was terminated, this
    class takes the error number and provides an error name and description as attributes.
    '''

    def __init__(self, idx):
        idx = str(idx)
        if (not idx in TERMINFO):
            idx = "0"
        # The name of the error as specified in lsbatch.h, for example TERM_RUNLIMIT
        self.name = TERMINFO[idx]['name']
        # Description of the error as specified in the LSF documenation.
        #  For example: "Job killed after reaching LSF run time limit"
        self.description = TERMINFO[idx]['desc']
        # The error number, for example: 5.
        self.number = int(TERMINFO[idx]['number'])
