# Queue priority calculation for Cogs

This app implements calculation of project priorities based on 
attributions as described in the paper circulated to the
Supercomputing Wales Infrastructure Committee.

In short, each project has a number of Attribution Points (APs)
gained from attributions entered into the system. These translate
to elevated QoS levels logarithmically, with time permitted to run
at the enhanced priority being proportional to the attribution level.


## Usage

The calculator is implemented as a `manage.py` command, accepting
two arguments: the filename of a pipe-delimited text file giving
output from `sacct` which will be used to calculate the priority, 
and the filename of a file in which to place the output, which
will be a comma-delimited text file containing project (Slurm Account)
codes and new Quality of Service values.

```shell
$ python manage.py calculate-priority slurm_dump.dat new_qoses.csv
```

This must then be integrated with Slurm. This can be done by creating
three Cron jobs. Two run on the cluster:

* At 12:01 every night, `sacct` is used to dump all queue data since
  an arbitrary point in time before prioritisation was implemented.
* At 12:59 every night, a shell script is used to apply updated priorities
  from the generated file to the Slurm Accounts (or to the QoS levels
  accessible to them).

The remaining job must be set up on the Cogs server:

* At 12:30 every night:
  * SCP the generated `sacct` dump to a staging directory on the Cogs server.
  * Call `calculate-priority` to act on the `sacct` dump and output
    to a CSV file in the staging area.
  * SCP the generated CSV file back to the cluster.

Passwordless SSH key-based access from the Cogs server to the cluster
must be set up for this to work. Usernames and filename conventions must
also be chosen.

The timings above have been chosen to happen relatively close to the middle
of the night, to allow enough time for each command to run even after
allowing for e.g. any clock skew between machines, and to avoid encountering
inconsistent behaviour during Daylight Savings Time changes (i.e. between
1am and 3am inclusively).
