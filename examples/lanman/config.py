"""This module contains all configuration information used to run simulations
"""
from multiprocessing import cpu_count
from collections import deque
import copy
from icarus.util import Tree

# GENERAL SETTINGS

# Level of logging output
# Available options: DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_LEVEL = 'INFO'

# If True, executes simulations in parallel using multiple processes
# to take advantage of multicore CPUs
PARALLEL_EXECUTION = True

# Number of processes used to run simulations in parallel.
# This option is ignored if PARALLEL_EXECUTION = False
N_PROCESSES = cpu_count()/3

# Granularity of caching.
# Currently, only OBJECT is supported
CACHING_GRANULARITY = 'OBJECT'

# Format in which results are saved.
# Result readers and writers are located in module ./icarus/results/readwrite.py
# Currently only PICKLE is supported 
RESULTS_FORMAT = 'PICKLE'

# Number of times each experiment is replicated
# This is necessary for extracting confidence interval of selected metrics
N_REPLICATIONS = 1

# List of metrics to be measured in the experiments
# The implementation of data collectors are located in ./icaurs/execution/collectors.py
DATA_COLLECTORS = ['SAT_RATE', 'CACHE_HIT_RATIO', 'LATENCY', 'OVERHEAD']

# Strategy that will be executed during warm-up phase
WARMUP_STRATEGY = 'NDN'

#Probability of caching
CACHING_PROBABILITY = 0.1

# This is a base experiment configuration with all the parameters that won't
# change across experiments of the same campaign
base = Tree()
base['network_model'] = Tree()
base['desc'] = "Base experiment"    # Description shown during execution

# Default experiment parameters
CACHE_POLICY = 'LRU'
# Alpha determines content selection (Zipf parameter)
ALPHA = 0.8
# Beta determines the zipf parameter determining how sources are selected
BETA = 0.9
# Number of content objects
N_CONTENTS = 10**4
# Number of content requests generated to prepopulate the caches
# These requests are not logged
N_WARMUP = 36*10**4 # 6 minutes
# Number of content requests generated after the warmup and logged
# to generate results. 
N_MEASURED = 36*10**5 # one hour
# Number of requests per second (over the whole network)
REQ_RATE = 1000

default = Tree()
default['workload'] = {
    'name':      'STATIONARY',
    'alpha':      ALPHA,
    'n_contents': N_CONTENTS,
    'n_warmup':   N_WARMUP,
    'n_measured': N_MEASURED,
    'rate':       REQ_RATE
    # 'beta':       BETA
                       }
default['content_placement']['name'] = 'LOWEST_DEGREE'
default['cache_policy']['name'] = CACHE_POLICY

# Instantiate experiment queue
EXPERIMENT_QUEUE = deque()

# C-FIB size sensitivity

base = copy.deepcopy(default)
# Total size of network cache as a fraction of content population
network_cache = 0.95 # 0.01
base['topology']['name'] = 'ROCKET_FUEL'
base['topology']['source_ratio'] = 0.1
base['topology']['ext_delay'] = 5 # 34
base['joint_cache_rsn_placement'] = {'network_cache': network_cache}
base['warmup_strategy']['name'] = WARMUP_STRATEGY
base['warmup_strategy']['p'] = CACHING_PROBABILITY

"""
2. SIT/DFIB size
"""
"""
for joint_cache_rsn_placement in ['CACHE_ALL_RSN_ALL']:
    for asn in [3257]:
        for rsn_cache_ratio in [2.0, 4.0, 8.0, 16.0, 32.0, 64.0, 128.0]:
            for strategy in ['LIRA_DFIB', 'LIRA_DFIB_OPH', 'LIRA_BC_HYBRID']:
                experiment = copy.deepcopy(base)
                experiment['topology']['asn'] = asn
                experiment['strategy']['name'] = strategy
                experiment['strategy']['p'] = CACHING_PROBABILITY
                experiment['joint_cache_rsn_placement']['name'] = joint_cache_rsn_placement
                experiment['joint_cache_rsn_placement']['network_rsn'] = rsn_cache_ratio * network_cache
                experiment['joint_cache_rsn_placement']['rsn_cache_ratio'] = rsn_cache_ratio
                experiment['desc'] = "RSN size sensitivity -> RSN/cache ratio: %s" % str(rsn_cache_ratio)
                EXPERIMENT_QUEUE.append(experiment)

"""

"""
3. latencyVSfreshness & cachehitsVSfreshness, etc.
"""

"""
for joint_cache_rsn_placement in ['CACHE_ALL_RSN_ALL']:
    for asn in [3257]:
        for fresh_interval in [10.0, 30.0, 60.0, 120.0, 180.0, 240.0, 300.0, 600.0, 1200.0]:
                experiment = copy.deepcopy(base)
                experiment['topology']['asn'] = asn
                experiment['strategy']['name'] = 'LIRA_BC_HYBRID'
                experiment['strategy']['p'] = CACHING_PROBABILITY
                experiment['strategy']['rsn_fresh'] = fresh_interval
                experiment['strategy']['extra_quota'] = 3
                experiment['joint_cache_rsn_placement']['name'] = joint_cache_rsn_placement
                experiment['joint_cache_rsn_placement']['network_rsn'] = 64* network_cache
                experiment['joint_cache_rsn_placement']['rsn_cache_ratio'] = 64
                experiment['desc'] = "RSN fresh_interval: %s" % str(fresh_interval)
                EXPERIMENT_QUEUE.append(experiment)
"""

"""
1. Extra Quota with Probability
"""

for joint_cache_rsn_placement in ['CACHE_ALL_RSN_ALL']:
    for strategy in ['LIRA_BC_HYBRID', 'LIRA_DFIB', 'LIRA_DFIB_OPH']:
        for caching_probability in [0.1, 0.25, 0.33, 0.5, 0.66, 0.75, 1.0]:
            for extra_quota in [0, 1, 2, 3, 4, 5]:
                experiment = copy.deepcopy(base)
                experiment['topology']['asn'] = 3257 #3967
                experiment['strategy']['name'] = strategy
                experiment['strategy']['rsn_fresh'] = 5.0
                experiment['strategy']['p'] = caching_probability 
                experiment['strategy']['extra_quota'] = extra_quota
                experiment['joint_cache_rsn_placement']['name'] = joint_cache_rsn_placement
                experiment['joint_cache_rsn_placement']['network_rsn'] = 64* network_cache
                experiment['joint_cache_rsn_placement']['rsn_cache_ratio'] = 64
                experiment['desc'] = "caching probability: %s" % str(caching_probability)
                EXPERIMENT_QUEUE.append(experiment)


"""
# experiments comparing different stragies 
for joint_cache_rsn_placement in ['CACHE_ALL_RSN_ALL']:
    for strategy in ['NDN', 'NRR_PROB', 'LIRA_BC']:    
        for caching_probability in [0.1, 0.25, 0.33, 0.5, 0.66, 0.75, 1.0]:
            experiment = copy.deepcopy(base)
            experiment['topology']['asn'] = 3257 #3967
            experiment['strategy']['name'] = strategy
            experiment['strategy']['p'] = caching_probability 
            experiment['joint_cache_rsn_placement']['name'] = joint_cache_rsn_placement
            experiment['joint_cache_rsn_placement']['network_rsn'] = 64* network_cache
            experiment['joint_cache_rsn_placement']['rsn_cache_ratio'] = 64
            experiment['desc'] = "caching probability: %s" % str(caching_probability)
            EXPERIMENT_QUEUE.append(experiment)
"""

"""
4th Experiments: Expiration time experiments
"""
"""
for joint_cache_rsn_placement in ['CACHE_ALL_RSN_ALL']:
    for strategy in ['LIRA_DFIB', 'LIRA_DFIB_OPH', 'LIRA_BC_HYBRID']:    
        for timeout in [5.0, 10.0, 30.0, 60.0, 120.0, 240.0, 360.0, 600.0, 1200.0, 3600.0, 7200.0]:
            experiment = copy.deepcopy(base)
            experiment['topology']['asn'] = 3257
            experiment['strategy']['name'] = strategy
            experiment['strategy']['p'] = CACHING_PROBABILITY
            experiment['strategy']['rsn_timeout'] = timeout 
            experiment['joint_cache_rsn_placement']['name'] = joint_cache_rsn_placement
            experiment['joint_cache_rsn_placement']['network_rsn'] = 64* network_cache
            experiment['joint_cache_rsn_placement']['rsn_cache_ratio'] = 64
            experiment['desc'] = "impact of timeout"
            EXPERIMENT_QUEUE.append(experiment)
"""
