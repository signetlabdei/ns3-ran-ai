from ctypes import *


# The environment is shared between ns-3
# and python with the same shared memory
# using the ns3-ai model.

class Env(Structure):
    _pack_ = 1
    _fields_ = [
        ('imsiStatsMap', (c_double * 28) * 50)
    ]


# The result is calculated by python
# and put back to ns-3 with the shared memory.

class Act(Structure):
    _pack_ = 1
    _fields_ = [
        ('actions', (c_int16 * 2) * 50)
    ]


mempool_key = 1234  # memory pool key, arbitrary integer large than 1000
mem_size = 40960  # memory pool size in bytes
memblock_key = 2333  # memory block key, need to keep the same in the ns-3 script


step_duration = 100  # Duration of a step [ms]
teleoperated_prr_requirement = .99
teleoperated_delay_requirement = 50000000  # [ns] 
mapsharing_prr_requirement = .99
mapsharing_delay_requirement = 100000000  # [ns]

cf_mean_per_action = {1150: 0.002492,
                      1450: 0.000044,
                      1451: 5.476881,
                      1452: 35.634660,
                      0: 0,
                      1: 5.476811,
                      2: 35.634485}
